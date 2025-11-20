#!/bin/bash

# Скрипт для обновления проекта на сервере
# Использование: ./update_server.sh

set -e

SERVER="152.42.186.191"
USER="root"
DEPLOY_PATH="/var/www/catalog"
# Попробуем найти SSH ключ автоматически
if [ -f ~/.ssh/id_ed25519 ]; then
    SSH_KEY="~/.ssh/id_ed25519"
elif [ -f ~/.ssh/id_rsa ]; then
    SSH_KEY="~/.ssh/id_rsa"
else
    SSH_KEY=""
fi

echo "🚀 Начинаем обновление проекта на сервере $SERVER"
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Функция для выполнения команд на сервере
run_remote() {
    ssh -o StrictHostKeyChecking=no ${USER}@${SERVER} "$1"
}

# Функция для проверки успешности команды
check_success() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1"
        exit 1
    fi
}

echo "📋 Этап 1: Резервное копирование"
echo "----------------------------"

# Создать директорию для бэкапов
run_remote "mkdir -p /root/backups/catalog"
check_success "Создана директория для бэкапов"

# Бэкап базы данных
BACKUP_DB="/root/backups/catalog/catalog_db_$(date +%Y%m%d_%H%M%S).sql"
run_remote "cd ${DEPLOY_PATH} && docker compose exec -T postgres pg_dump -U catalog_user catalog_db > ${BACKUP_DB}"
check_success "Создана резервная копия базы данных: ${BACKUP_DB}"

# Бэкап конфигурации
BACKUP_ENV="/root/backups/catalog/catalog_env_$(date +%Y%m%d_%H%M%S).env"
run_remote "cp ${DEPLOY_PATH}/backend/.env ${BACKUP_ENV}"
check_success "Создана резервная копия .env: ${BACKUP_ENV}"

BACKUP_COMPOSE="/root/backups/catalog/catalog_compose_$(date +%Y%m%d_%H%M%S).yml"
run_remote "cp ${DEPLOY_PATH}/docker-compose.yml ${BACKUP_COMPOSE}"
check_success "Создана резервная копия docker-compose.yml: ${BACKUP_COMPOSE}"

echo ""
echo "📦 Этап 2: Сохранение локальных изменений"
echo "----------------------------"

# Сохранить diff requirements.txt если есть изменения
run_remote "cd ${DEPLOY_PATH} && git diff backend/requirements.txt > /root/backups/catalog/requirements_diff_$(date +%Y%m%d_%H%M%S).patch 2>/dev/null || true"
check_success "Сохранен diff requirements.txt (если были изменения)"

echo ""
echo "🔄 Этап 3: Обновление кода"
echo "----------------------------"

# Получить последние изменения
run_remote "cd ${DEPLOY_PATH} && git fetch origin"
check_success "Получены изменения из git"

# Проверить текущий коммит
CURRENT_COMMIT=$(run_remote "cd ${DEPLOY_PATH} && git rev-parse HEAD")
echo "Текущий коммит: ${CURRENT_COMMIT}"

# Обновить код
run_remote "cd ${DEPLOY_PATH} && git pull origin main"
check_success "Код обновлен"

NEW_COMMIT=$(run_remote "cd ${DEPLOY_PATH} && git rev-parse HEAD")
echo "Новый коммит: ${NEW_COMMIT}"

echo ""
echo "🔧 Этап 4: Проверка зависимостей"
echo "----------------------------"

# Проверить, нужен ли psycopg2-binary (должен быть в новом коде)
HAS_PSYCOPG=$(run_remote "cd ${DEPLOY_PATH} && grep -q 'psycopg2-binary' backend/requirements.txt && echo 'yes' || echo 'no'")

if [ "$HAS_PSYCOPG" = "yes" ]; then
    echo -e "${GREEN}✓${NC} psycopg2-binary присутствует в requirements.txt"
else
    echo -e "${YELLOW}⚠${NC} psycopg2-binary отсутствует, добавляем..."
    run_remote "cd ${DEPLOY_PATH} && echo 'psycopg2-binary==2.9.9' >> backend/requirements.txt"
    check_success "Добавлен psycopg2-binary в requirements.txt"
fi

echo ""
echo "🐳 Этап 5: Обновление контейнеров"
echo "----------------------------"

# Остановить контейнеры
echo "Останавливаем контейнеры..."
run_remote "cd ${DEPLOY_PATH} && docker compose down"
check_success "Контейнеры остановлены"

# Пересобрать образы
echo "Пересобираем образы..."
run_remote "cd ${DEPLOY_PATH} && docker compose build --no-cache"
check_success "Образы пересобраны"

# Запустить контейнеры
echo "Запускаем контейнеры..."
run_remote "cd ${DEPLOY_PATH} && docker compose --profile production up -d"
check_success "Контейнеры запущены"

# Подождать немного для инициализации
echo "Ожидание инициализации контейнеров..."
sleep 10

echo ""
echo "✅ Этап 6: Проверка работоспособности"
echo "----------------------------"

# Проверить статус контейнеров
echo "Статус контейнеров:"
run_remote "cd ${DEPLOY_PATH} && docker compose ps"

# Проверить health backend
HEALTH=$(run_remote "cd ${DEPLOY_PATH} && docker compose ps --format json backend | grep -o '\"Health\":\"[^\"]*\"' | cut -d'\"' -f4")
if [ "$HEALTH" = "healthy" ]; then
    echo -e "${GREEN}✓${NC} Backend контейнер healthy"
else
    echo -e "${YELLOW}⚠${NC} Backend контейнер: ${HEALTH}"
fi

# Проверить API
API_RESPONSE=$(run_remote "curl -s http://localhost:8000/health || echo 'ERROR'")
if [ "$API_RESPONSE" != "ERROR" ]; then
    echo -e "${GREEN}✓${NC} API отвечает: ${API_RESPONSE}"
else
    echo -e "${YELLOW}⚠${NC} API не отвечает, проверьте логи"
fi

# Проверить базу данных
DB_CHECK=$(run_remote "cd ${DEPLOY_PATH} && docker compose exec -T backend python -c 'from app.database import SessionLocal; from app.models import Dessert, User; db = SessionLocal(); print(f\"Desserts: {db.query(Dessert).count()}, Users: {db.query(User).count()}\"); db.close()' 2>&1")
echo "База данных: ${DB_CHECK}"

echo ""
echo "🧹 Этап 7: Очистка старых файлов"
echo "----------------------------"

# Удалить старые dev-файлы
FILES_TO_REMOVE=(
    "docker-compose.dev.yml"
    "docker-compose.override.yml.example"
    "start-docker.sh"
    "backend/init_db.py"
    "INIT_DATA.md"
    "PRODUCTION_CHECKLIST.md"
    "QUICKSTART_DOCKER.md"
    "SECURITY_AUDIT.md"
)

for file in "${FILES_TO_REMOVE[@]}"; do
    run_remote "cd ${DEPLOY_PATH} && rm -f ${file} && echo 'Removed: ${file}' || echo 'Not found: ${file}'"
done

# Проверить наличие нового файла
if run_remote "cd ${DEPLOY_PATH} && test -f backend/init_prod_db.py"; then
    echo -e "${GREEN}✓${NC} Новый файл init_prod_db.py на месте"
else
    echo -e "${RED}✗${NC} Файл init_prod_db.py не найден!"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Обновление завершено успешно!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo "📊 Резюме:"
echo "  - Резервные копии: /root/backups/catalog/"
echo "  - База данных: ${DB_CHECK}"
echo "  - API статус: ${API_RESPONSE}"
echo ""
echo "🔍 Для проверки логов:"
echo "  ssh ${USER}@${SERVER} 'cd ${DEPLOY_PATH} && docker compose logs --tail=50 backend'"
echo ""
echo "🔄 Для отката (если нужно):"
echo "  ssh ${USER}@${SERVER}"
echo "  cd ${DEPLOY_PATH}"
echo "  docker compose down"
echo "  docker compose exec postgres psql -U catalog_user catalog_db < ${BACKUP_DB}"
echo "  docker compose --profile production up -d"

