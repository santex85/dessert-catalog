#!/bin/bash

# Скрипт для запуска Docker Compose с ожиданием стабилизации Docker
# Использование: ./start-docker.sh [--skip-port-check]

set -e

# Проверяем флаг пропуска проверки портов
SKIP_PORT_CHECK=false
if [ "$1" = "--skip-port-check" ]; then
    SKIP_PORT_CHECK=true
fi

# Проверяем, запущен ли Docker Desktop процесс
if ! pgrep -f "Docker Desktop" > /dev/null; then
    echo "⚠️  Docker Desktop не запущен. Запускаю..."
    open -a Docker
    echo "⏳ Ожидание запуска Docker Desktop..."
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
        
        # Показываем прогресс только каждые 5 попыток
        if [ $((ATTEMPT % 5)) -eq 0 ]; then
            echo "   Ожидание... ($ATTEMPT/$MAX_ATTEMPTS)"
        fi
        sleep 2
        ATTEMPT=$((ATTEMPT + 1))
    done
fi

# Освобождаем порты, если они заняты
if [ "$SKIP_PORT_CHECK" = true ]; then
    PORTS_FREED=false
else
    PORTS_FREED=false

    # Функция для безопасного освобождения порта
    free_port() {
    local PORT=$1
    local PORT_NAME=$2
    
    # Сначала проверяем, не занят ли порт Docker контейнерами
    if check_docker_daemon; then
        local CONTAINER=$(docker ps --format "{{.Names}}" --filter "publish=$PORT" 2>/dev/null | head -1)
        if [ -n "$CONTAINER" ]; then
            echo "⚠️  Порт $PORT_NAME занят контейнером: $CONTAINER. Останавливаю..."
            docker stop "$CONTAINER" 2>/dev/null || true
            sleep 1
            PORTS_FREED=true
            return
        fi
    fi
    
    # Если не Docker контейнер, проверяем локальные процессы
    if lsof -ti:$PORT >/dev/null 2>&1; then
        echo "⚠️  Порт $PORT_NAME занят. Освобождаю..."
        lsof -ti:$PORT | xargs kill -TERM 2>/dev/null || true
        sleep 2
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
    echo "⏳ Ожидание стабилизации Docker..."
    i=1
    while [ $i -le 10 ]; do
        if check_docker_daemon; then
            break
        fi
        if [ $i -eq 10 ]; then
            echo "❌ Docker daemon недоступен"
            echo "Попробуйте: open -a Docker и подождите 30-60 секунд"
            exit 1
        fi
        if [ $((i % 5)) -eq 0 ]; then
            echo "   Ожидание... ($i/10)"
        fi
        sleep 2
        i=$((i + 1))
    done
fi

# Останавливаем старые контейнеры, если они есть
if check_docker_daemon && docker compose ps 2>/dev/null | grep -q "Up\|running"; then
    echo "🧹 Остановка старых контейнеров..."
    docker compose down 2>/dev/null || true
    sleep 3
    # Проверяем Docker daemon снова
    i=1
    while [ $i -le 5 ]; do
        if check_docker_daemon; then
            break
        fi
        if [ $i -eq 5 ]; then
            echo "❌ Docker daemon недоступен"
            echo "Попробуйте: open -a Docker и подождите 30 секунд"
            exit 1
        fi
        sleep 2
        i=$((i + 1))
    done
fi

# Финальная проверка перед запуском
if ! check_docker_daemon; then
    echo "❌ Docker daemon недоступен"
    echo "Попробуйте: open -a Docker и подождите 30-60 секунд"
    exit 1
fi

# Запускаем контейнеры
echo "🚀 Запуск Docker Compose..."
docker compose up -d

echo ""
echo "✅ Готово!"
echo "🌐 Frontend: http://localhost:3000"
echo "🌐 Backend:  http://localhost:8000"
echo "📋 Логи: docker compose logs -f"

