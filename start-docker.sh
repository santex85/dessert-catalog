#!/bin/bash

# Скрипт для запуска Docker Compose с ожиданием стабилизации Docker
# Использование: ./start-docker.sh [--skip-port-check]

set -e

# Проверяем флаг пропуска проверки портов
SKIP_PORT_CHECK=false
if [ "$1" = "--skip-port-check" ]; then
    SKIP_PORT_CHECK=true
fi

echo "🔍 Проверка Docker Desktop..."

# Проверяем, запущен ли Docker Desktop процесс
if ! pgrep -f "Docker Desktop" > /dev/null; then
    echo "⚠️  Docker Desktop не запущен. Запускаю..."
    open -a Docker
    echo "⏳ Ожидание запуска Docker Desktop (это может занять 30-60 секунд)..."
    sleep 10
fi

# Функция проверки Docker daemon (проверяем наличие Server секции)
check_docker_daemon() {
    docker info 2>&1 | grep -q "^Server:" && ! docker info 2>&1 | grep -q "Cannot connect"
}

# Проверяем Docker daemon (быстрая проверка)
if check_docker_daemon; then
    echo "✅ Docker daemon доступен!"
else
    echo "⏳ Ожидание Docker daemon..."
    MAX_ATTEMPTS=15
    ATTEMPT=1
    
    while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
        if check_docker_daemon; then
            echo "✅ Docker daemon доступен!"
            break
        fi
        
        if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
            echo "❌ Docker daemon недоступен после $MAX_ATTEMPTS попыток"
            echo ""
            echo "Попробуйте:"
            echo "  1. Открыть Docker Desktop вручную: open -a Docker"
            echo "  2. Подождать 30-60 секунд, пока он полностью загрузится"
            echo "  3. Проверить: docker info"
            echo "  4. Запустить напрямую: docker compose up -d"
            exit 1
        fi
        
        # Показываем прогресс только каждые 3 попытки
        if [ $((ATTEMPT % 3)) -eq 0 ]; then
            echo "   Ожидание... (попытка $ATTEMPT/$MAX_ATTEMPTS)"
        fi
        sleep 2
        ATTEMPT=$((ATTEMPT + 1))
    done
fi

# Освобождаем порты, если они заняты
if [ "$SKIP_PORT_CHECK" = true ]; then
    echo "⏭️  Пропуск проверки портов (--skip-port-check)"
    PORTS_FREED=false
else
    echo "🔍 Проверка портов..."
    PORTS_FREED=false

    # Функция для безопасного освобождения порта
    free_port() {
    local PORT=$1
    local PORT_NAME=$2
    
    # Сначала проверяем, не занят ли порт Docker контейнерами
    if check_docker_daemon; then
        local CONTAINER=$(docker ps --format "{{.Names}}" --filter "publish=$PORT" 2>/dev/null | head -1)
        if [ -n "$CONTAINER" ]; then
            echo "⚠️  Порт $PORT_NAME занят Docker контейнером: $CONTAINER"
            echo "   Останавливаю контейнер через Docker..."
            docker stop "$CONTAINER" 2>/dev/null || true
            sleep 1
            PORTS_FREED=true
            return
        fi
    fi
    
    # Если не Docker контейнер, проверяем локальные процессы
    if lsof -ti:$PORT >/dev/null 2>&1; then
        echo "⚠️  Порт $PORT_NAME занят локальным процессом. Освобождаю..."
        # Более мягкое завершение - сначала SIGTERM, потом SIGKILL
        lsof -ti:$PORT | xargs kill -TERM 2>/dev/null || true
        sleep 2
        # Если процесс еще жив, убиваем принудительно
        if lsof -ti:$PORT >/dev/null 2>&1; then
            lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
            sleep 1
        fi
        PORTS_FREED=true
    fi
}

    # Освобождаем порты
    free_port 8000 "8000"
    free_port 3000 "3000"
fi

# Если освобождали порты через kill (не через Docker), проверяем daemon
if [ "$PORTS_FREED" = true ] && ! check_docker_daemon; then
    echo "⏳ Проверка Docker daemon после освобождения портов..."
    i=1
    while [ $i -le 10 ]; do
        if check_docker_daemon; then
            echo "✅ Docker daemon снова доступен!"
            break
        fi
        if [ $i -eq 10 ]; then
            echo "❌ Docker daemon недоступен после освобождения портов"
            echo ""
            echo "Попробуйте:"
            echo "  1. Открыть Docker Desktop: open -a Docker"
            echo "  2. Подождать 30-60 секунд"
            echo "  3. Проверить: docker info"
            echo "  4. Запустить напрямую: docker compose up -d"
            exit 1
        fi
        if [ $((i % 3)) -eq 0 ]; then
            echo "   Ожидание... (попытка $i/10)"
        fi
        sleep 2
        i=$((i + 1))
    done
fi

# Останавливаем старые контейнеры, если они есть
echo "🧹 Очистка старых контейнеров..."
if check_docker_daemon && docker compose ps 2>/dev/null | grep -q "Up\|running"; then
    docker compose down 2>/dev/null || true
    echo "⏳ Ожидание стабилизации Docker после остановки контейнеров..."
    sleep 3
    # Проверяем Docker daemon снова
    i=1
    while [ $i -le 5 ]; do
        if check_docker_daemon; then
            echo "✅ Docker daemon снова доступен!"
            break
        fi
        if [ $i -eq 5 ]; then
            echo "❌ Docker daemon недоступен после остановки контейнеров"
            echo "Попробуйте запустить Docker Desktop вручную и подождать 30 секунд"
            exit 1
        fi
        echo "   Ожидание Docker daemon... (попытка $i/5)"
        sleep 2
        i=$((i + 1))
    done
else
    echo "   Нет запущенных контейнеров"
fi

# Финальная проверка перед запуском
if ! check_docker_daemon; then
    echo "❌ Docker daemon недоступен перед запуском контейнеров"
    echo "Попробуйте:"
    echo "  1. Открыть Docker Desktop: open -a Docker"
    echo "  2. Подождать 30-60 секунд"
    echo "  3. Запустить: docker compose up -d"
    exit 1
fi

# Запускаем контейнеры
echo "🚀 Запуск Docker Compose..."
docker compose up -d

echo "✅ Готово!"
echo ""
echo "📊 Статус контейнеров:"
docker compose ps

echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🌐 Backend:  http://localhost:8000"
echo ""
echo "📋 Логи: docker compose logs -f"

