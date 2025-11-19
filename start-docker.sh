#!/bin/bash

# Скрипт для запуска Docker Compose с ожиданием стабилизации Docker

set -e

echo "🔍 Проверка Docker Desktop..."

# Проверяем, запущен ли Docker Desktop
if ! pgrep -f "Docker Desktop" > /dev/null; then
    echo "⚠️  Docker Desktop не запущен. Запускаю..."
    open -a Docker
    echo "⏳ Ожидание запуска Docker Desktop (это может занять 30-60 секунд)..."
    sleep 10
fi

# Ждем, пока Docker daemon станет доступен
echo "⏳ Ожидание Docker daemon..."
MAX_ATTEMPTS=30
ATTEMPT=1

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    if docker info >/dev/null 2>&1; then
        echo "✅ Docker daemon доступен!"
        break
    fi
    
    if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
        echo "❌ Docker daemon недоступен после $MAX_ATTEMPTS попыток"
        echo "Попробуйте:"
        echo "  1. Открыть Docker Desktop вручную"
        echo "  2. Подождать, пока он полностью загрузится"
        echo "  3. Запустить: docker compose up -d"
        exit 1
    fi
    
    echo "   Попытка $ATTEMPT/$MAX_ATTEMPTS..."
    sleep 2
    ATTEMPT=$((ATTEMPT + 1))
done

# Освобождаем порты, если они заняты
echo "🔍 Проверка портов..."
if lsof -ti:8000 >/dev/null 2>&1; then
    echo "⚠️  Порт 8000 занят. Освобождаю..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

if lsof -ti:3000 >/dev/null 2>&1; then
    echo "⚠️  Порт 3000 занят. Освобождаю..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Останавливаем старые контейнеры, если они есть
echo "🧹 Очистка старых контейнеров..."
docker compose down 2>/dev/null || true

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

