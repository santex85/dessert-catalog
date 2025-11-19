.PHONY: help install install-backend install-frontend init-db run run-backend run-frontend clean clean-backend clean-frontend restart test docker-up docker-down docker-build docker-logs docker-init-db deploy deploy-check deploy-remote deploy-status deploy-logs deploy-shell docker-stop-conflicts docker-check

# Переменные
PYTHON := python3
PIP := pip
NPM := npm
VENV := backend/venv
VENV_BIN := $(VENV)/bin
BACKEND_DIR := backend
FRONTEND_DIR := frontend
# Docker Compose command (use 'docker compose' if docker-compose not found)
DOCKER_COMPOSE := $(shell command -v docker-compose >/dev/null 2>&1 && echo docker-compose || echo docker compose)

# Цвета для вывода
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help: ## Показать справку по командам
	@echo "$(GREEN)Доступные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: install-backend install-frontend ## Установить все зависимости

install-backend: ## Установить зависимости бэкенда
	@echo "$(GREEN)Установка зависимостей бэкенда...$(NC)"
	@if [ ! -d "$(VENV)" ]; then \
		echo "Создание виртуального окружения..."; \
		$(PYTHON) -m venv $(VENV); \
	fi
	@$(VENV_BIN)/pip install --upgrade pip
	@$(VENV_BIN)/pip install -r $(BACKEND_DIR)/requirements.txt
	@echo "$(GREEN)✓ Зависимости бэкенда установлены$(NC)"

install-frontend: ## Установить зависимости фронтенда
	@echo "$(GREEN)Установка зависимостей фронтенда...$(NC)"
	@cd $(FRONTEND_DIR) && $(NPM) install
	@echo "$(GREEN)✓ Зависимости фронтенда установлены$(NC)"

init-db: ## Инициализировать базу данных с тестовыми данными
	@echo "$(GREEN)Инициализация базы данных...$(NC)"
	@$(VENV_BIN)/python $(BACKEND_DIR)/init_db.py
	@echo "$(GREEN)✓ База данных инициализирована$(NC)"

run: run-backend run-frontend ## Запустить бэкенд и фронтенд (в фоне)

run-backend: ## Запустить только бэкенд
	@echo "$(GREEN)Запуск бэкенд-сервера...$(NC)"
	@cd $(BACKEND_DIR) && $(VENV_BIN)/uvicorn main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Запустить только фронтенд
	@echo "$(GREEN)Запуск фронтенд-сервера...$(NC)"
	@cd $(FRONTEND_DIR) && $(NPM) run dev

run-backend-bg: ## Запустить бэкенд в фоновом режиме
	@echo "$(GREEN)Запуск бэкенд-сервера в фоне...$(NC)"
	@cd $(BACKEND_DIR) && nohup $(VENV_BIN)/uvicorn main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 & echo $$! > backend.pid
	@echo "$(GREEN)✓ Бэкенд запущен (PID: $$(cat $(BACKEND_DIR)/backend.pid))$(NC)"
	@echo "Логи: tail -f $(BACKEND_DIR)/backend.log"

run-frontend-bg: ## Запустить фронтенд в фоновом режиме
	@echo "$(GREEN)Запуск фронтенд-сервера в фоне...$(NC)"
	@cd $(FRONTEND_DIR) && nohup $(NPM) run dev > frontend.log 2>&1 & echo $$! > frontend.pid
	@echo "$(GREEN)✓ Фронтенд запущен (PID: $$(cat $(FRONTEND_DIR)/frontend.pid))$(NC)"
	@echo "Логи: tail -f $(FRONTEND_DIR)/frontend.log"

run-all-bg: run-backend-bg run-frontend-bg ## Запустить всё в фоновом режиме
	@echo "$(GREEN)✓ Все сервисы запущены в фоне$(NC)"
	@echo "$(YELLOW)Бэкенд:$(NC) http://localhost:8000"
	@echo "$(YELLOW)Фронтенд:$(NC) http://localhost:3000"
	@echo "$(YELLOW)API Docs:$(NC) http://localhost:8000/docs"

stop: ## Остановить все фоновые процессы
	@echo "$(GREEN)Остановка сервисов...$(NC)"
	@if [ -f "$(BACKEND_DIR)/backend.pid" ]; then \
		kill $$(cat $(BACKEND_DIR)/backend.pid) 2>/dev/null || true; \
		rm $(BACKEND_DIR)/backend.pid; \
		echo "$(GREEN)✓ Бэкенд остановлен$(NC)"; \
	fi
	@if [ -f "$(FRONTEND_DIR)/frontend.pid" ]; then \
		kill $$(cat $(FRONTEND_DIR)/frontend.pid) 2>/dev/null || true; \
		rm $(FRONTEND_DIR)/frontend.pid; \
		echo "$(GREEN)✓ Фронтенд остановлен$(NC)"; \
	fi

restart: stop run-all-bg ## Перезапустить все сервисы

setup: install init-db ## Полная настройка проекта (установка + инициализация БД)
	@echo "$(GREEN)✓ Проект готов к запуску!$(NC)"
	@echo "$(YELLOW)Запустите:$(NC) make run-all-bg"

clean: clean-backend clean-frontend ## Очистить все временные файлы

clean-backend: ## Очистить файлы бэкенда
	@echo "$(GREEN)Очистка бэкенда...$(NC)"
	@find $(BACKEND_DIR) -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	@find $(BACKEND_DIR) -type f -name "*.pyc" -delete 2>/dev/null || true
	@find $(BACKEND_DIR) -type f -name "*.pyo" -delete 2>/dev/null || true
	@rm -f $(BACKEND_DIR)/*.log $(BACKEND_DIR)/*.pid
	@rm -f $(BACKEND_DIR)/catalog.db $(BACKEND_DIR)/catalog.db-journal
	@echo "$(GREEN)✓ Бэкенд очищен$(NC)"

clean-frontend: ## Очистить файлы фронтенда
	@echo "$(GREEN)Очистка фронтенда...$(NC)"
	@cd $(FRONTEND_DIR) && rm -rf node_modules dist build .vite 2>/dev/null || true
	@rm -f $(FRONTEND_DIR)/*.log $(FRONTEND_DIR)/*.pid
	@echo "$(GREEN)✓ Фронтенд очищен$(NC)"

clean-all: clean ## Полная очистка (включая venv и node_modules)
	@echo "$(GREEN)Полная очистка...$(NC)"
	@rm -rf $(VENV)
	@cd $(FRONTEND_DIR) && rm -rf node_modules
	@echo "$(GREEN)✓ Полная очистка завершена$(NC)"

test-backend: ## Запустить тесты бэкенда
	@echo "$(GREEN)Запуск тестов бэкенда...$(NC)"
	@$(VENV_BIN)/pytest $(BACKEND_DIR)/tests/ -v || echo "$(YELLOW)Тесты не найдены$(NC)"

test-frontend: ## Запустить тесты фронтенда
	@echo "$(GREEN)Запуск тестов фронтенда...$(NC)"
	@cd $(FRONTEND_DIR) && $(NPM) test || echo "$(YELLOW)Тесты не настроены$(NC)"

logs-backend: ## Показать логи бэкенда
	@tail -f $(BACKEND_DIR)/backend.log 2>/dev/null || echo "$(YELLOW)Логи не найдены. Запустите: make run-backend-bg$(NC)"

logs-frontend: ## Показать логи фронтенда
	@tail -f $(FRONTEND_DIR)/frontend.log 2>/dev/null || echo "$(YELLOW)Логи не найдены. Запустите: make run-frontend-bg$(NC)"

status: ## Показать статус сервисов
	@echo "$(GREEN)Статус сервисов:$(NC)"
	@if [ -f "$(BACKEND_DIR)/backend.pid" ]; then \
		if ps -p $$(cat $(BACKEND_DIR)/backend.pid) > /dev/null 2>&1; then \
			echo "$(GREEN)✓ Бэкенд:$(NC) запущен (PID: $$(cat $(BACKEND_DIR)/backend.pid))"; \
		else \
			echo "$(YELLOW)✗ Бэкенд:$(NC) не запущен"; \
		fi \
	else \
		echo "$(YELLOW)✗ Бэкенд:$(NC) не запущен"; \
	fi
	@if [ -f "$(FRONTEND_DIR)/frontend.pid" ]; then \
		if ps -p $$(cat $(FRONTEND_DIR)/frontend.pid) > /dev/null 2>&1; then \
			echo "$(GREEN)✓ Фронтенд:$(NC) запущен (PID: $$(cat $(FRONTEND_DIR)/frontend.pid))"; \
		else \
			echo "$(YELLOW)✗ Фронтенд:$(NC) не запущен"; \
		fi \
	else \
		echo "$(YELLOW)✗ Фронтенд:$(NC) не запущен"; \
	fi
	@echo ""
	@echo "$(YELLOW)URLs:$(NC)"
	@echo "  Бэкенд:    http://localhost:8000"
	@echo "  Фронтенд:  http://localhost:3000"
	@echo "  API Docs:  http://localhost:8000/docs"
	@echo ""
	@echo "$(GREEN)Docker Compose команды:$(NC)"
	@echo "  docker-up       - Запустить все сервисы в Docker"
	@echo "  docker-up-prod  - Запустить с PostgreSQL (production)"
	@echo "  docker-down     - Остановить все сервисы"
	@echo "  docker-build    - Пересобрать контейнеры"
	@echo "  docker-logs     - Показать логи"
	@echo "  docker-init-db  - Инициализировать базу данных"
	@echo ""
	@echo "$(GREEN)Deployment команды:$(NC)"
	@echo "  deploy          - Deploy to remote server"
	@echo "  deploy-status   - Check remote server status"
	@echo "  deploy-logs     - View remote server logs"
	@echo "  deploy-shell    - Open shell on remote server"

# Docker Compose commands
docker-check: ## Проверить, что Docker запущен
	@echo "$(YELLOW)Проверка Docker daemon...$(NC)"
	@if ! docker info >/dev/null 2>&1; then \
		echo "$(YELLOW)⚠ Docker daemon не запущен!$(NC)"; \
		echo "$(YELLOW)Запустите Docker Desktop или выполните:$(NC)"; \
		echo "  open -a Docker"; \
		echo ""; \
		echo "$(YELLOW)Подождите, пока Docker полностью запустится, затем попробуйте снова.$(NC)"; \
		exit 1; \
	fi
	@if ! $(DOCKER_COMPOSE) version >/dev/null 2>&1; then \
		echo "$(YELLOW)⚠ docker compose не доступен!$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ Docker daemon запущен$(NC)"

docker-stop-conflicts: docker-check ## Остановить процессы, конфликтующие с Docker
	@echo "$(YELLOW)Проверка конфликтов портов...$(NC)"
	@if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then \
		echo "$(YELLOW)⚠ Порт 8000 занят. Останавливаю локальные процессы...$(NC)"; \
		$(MAKE) stop || true; \
		lsof -ti:8000 | xargs kill -9 2>/dev/null || true; \
		sleep 1; \
	fi
	@if docker info >/dev/null 2>&1; then \
		if docker ps --format '{{.Ports}}' 2>/dev/null | grep -q ':8000->'; then \
			echo "$(YELLOW)⚠ Порт 8000 занят Docker контейнером. Останавливаю...$(NC)"; \
			$(DOCKER_COMPOSE) down 2>/dev/null || true; \
			sleep 2; \
		fi; \
		if docker ps --format '{{.Ports}}' 2>/dev/null | grep -q ':3000->'; then \
			echo "$(YELLOW)⚠ Порт 3000 занят Docker контейнером. Останавливаю...$(NC)"; \
			$(DOCKER_COMPOSE) down 2>/dev/null || true; \
			sleep 2; \
		fi; \
	fi
	@echo "$(GREEN)✓ Конфликты разрешены$(NC)"

docker-up: docker-check docker-stop-conflicts ## Запустить все сервисы в Docker
	@echo "$(GREEN)Запуск Docker Compose...$(NC)"
	@if [ ! -f "$(BACKEND_DIR)/.env" ]; then \
		echo "$(YELLOW)Создание backend/.env из env.example...$(NC)"; \
		cp $(BACKEND_DIR)/env.example $(BACKEND_DIR)/.env; \
		echo "$(YELLOW)⚠ ВАЖНО: Отредактируйте backend/.env и установите SECRET_KEY!$(NC)"; \
	fi
	@echo "$(YELLOW)Проверка подключения к Docker перед запуском...$(NC)"
	@i=1; \
	while [ $$i -le 5 ]; do \
		if docker info >/dev/null 2>&1; then \
			echo "$(GREEN)✓ Docker готов$(NC)"; \
			break; \
		fi; \
		if [ $$i -eq 5 ]; then \
			echo "$(YELLOW)⚠ Docker daemon недоступен после 5 попыток!$(NC)"; \
			echo "$(YELLOW)Попробуйте запустить Docker Desktop: open -a Docker$(NC)"; \
			echo "$(YELLOW)Или проверьте статус: docker info$(NC)"; \
			exit 1; \
		fi; \
		echo "$(YELLOW)Ожидание Docker daemon... (попытка $$i/5)$(NC)"; \
		sleep 2; \
		i=$$((i + 1)); \
	done
	@$(DOCKER_COMPOSE) up -d || { \
		echo "$(YELLOW)⚠ Ошибка при запуске $(DOCKER_COMPOSE).$(NC)"; \
		echo "$(YELLOW)Проверьте:$(NC)"; \
		echo "  1. Docker Desktop запущен: open -a Docker"; \
		echo "  2. Docker daemon готов: docker info"; \
		echo "  3. $(DOCKER_COMPOSE) доступен: $(DOCKER_COMPOSE) version"; \
		exit 1; \
	}
	@echo "$(GREEN)✓ Сервисы запущены$(NC)"
	@echo "$(YELLOW)Frontend:$(NC) http://localhost:3000"
	@echo "$(YELLOW)Backend:$(NC) http://localhost:8000"

docker-up-prod: docker-check ## Запустить с PostgreSQL (production)
	@echo "$(GREEN)Запуск Docker Compose с PostgreSQL...$(NC)"
	@if [ ! -f "$(BACKEND_DIR)/.env" ]; then \
		echo "$(YELLOW)Создание backend/.env из env.example...$(NC)"; \
		cp $(BACKEND_DIR)/env.example $(BACKEND_DIR)/.env; \
		echo "$(YELLOW)⚠ ВАЖНО: Отредактируйте backend/.env!$(NC)"; \
	fi
	@$(DOCKER_COMPOSE) --profile production up -d
	@echo "$(GREEN)✓ Сервисы запущены с PostgreSQL$(NC)"

docker-down: docker-check ## Остановить все Docker сервисы
	@echo "$(GREEN)Остановка Docker Compose...$(NC)"
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ Сервисы остановлены$(NC)"

docker-build: docker-check ## Пересобрать Docker контейнеры
	@echo "$(GREEN)Пересборка контейнеров...$(NC)"
	@$(DOCKER_COMPOSE) build --no-cache
	@echo "$(GREEN)✓ Контейнеры пересобраны$(NC)"

docker-logs: ## Показать логи Docker сервисов
	@$(DOCKER_COMPOSE) logs -f

docker-init-db: ## Инициализировать базу данных в Docker
	@echo "$(GREEN)Инициализация базы данных...$(NC)"
	@$(DOCKER_COMPOSE) exec backend python init_db.py
	@echo "$(GREEN)✓ База данных инициализирована$(NC)"

docker-shell-backend: ## Открыть shell в backend контейнере
	@$(DOCKER_COMPOSE) exec backend bash

docker-shell-frontend: ## Открыть shell в frontend контейнере
	@$(DOCKER_COMPOSE) exec frontend sh

docker-restart: ## Перезапустить Docker сервисы
	@$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)✓ Сервисы перезапущены$(NC)"

# Deployment commands
deploy: ## Deploy to remote server
	@if [ ! -f "deploy.env" ]; then \
		echo "$(YELLOW)⚠ deploy.env not found. Creating from template...$(NC)"; \
		cp deploy.env.example deploy.env; \
		echo "$(YELLOW)⚠ Please edit deploy.env with your server details and run make deploy again$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Starting deployment...$(NC)"
	@$(MAKE) deploy-check
	@$(MAKE) deploy-remote

deploy-check: ## Check deployment configuration
	@echo "$(GREEN)Checking deployment configuration...$(NC)"
	@if [ ! -f "deploy.env" ]; then \
		echo "$(YELLOW)⚠ deploy.env not found$(NC)"; \
		exit 1; \
	fi
	@. deploy.env && \
	if [ -z "$$DEPLOY_HOST" ] || [ -z "$$DEPLOY_USER" ] || [ -z "$$DEPLOY_PATH" ]; then \
		echo "$(YELLOW)⚠ Missing required variables in deploy.env$(NC)"; \
		echo "Required: DEPLOY_HOST, DEPLOY_USER, DEPLOY_PATH"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ Configuration valid$(NC)"

deploy-remote: ## Execute deployment on remote server
	@. deploy.env && \
	SSH_KEY_OPT=$$([ -n "$$DEPLOY_KEY" ] && echo "-i $$DEPLOY_KEY" || echo ""); \
	SSH_PORT_OPT=$$([ -n "$$DEPLOY_PORT" ] && echo "-p $$DEPLOY_PORT" || echo ""); \
	COMPOSE_FILE=$${DEPLOY_COMPOSE_FILE:-$(DOCKER_COMPOSE).yml}; \
	PROFILE_OPT=$$([ -n "$$DEPLOY_PROFILE" ] && echo "--profile $$DEPLOY_PROFILE" || echo ""); \
	BRANCH=$${DEPLOY_BRANCH:-main}; \
	echo "$(GREEN)Connecting to $$DEPLOY_USER@$$DEPLOY_HOST...$(NC)"; \
	ssh $$SSH_KEY_OPT $$SSH_PORT_OPT $$DEPLOY_USER@$$DEPLOY_HOST " \
		set -e && \
		cd $$DEPLOY_PATH || { echo 'Directory $$DEPLOY_PATH not found!'; exit 1; } && \
		echo '✓ Connected to server' && \
		echo 'Pulling latest changes...' && \
		git fetch origin || echo '⚠ Git fetch failed (continuing...)' && \
		git checkout $$BRANCH || echo '⚠ Branch checkout failed (continuing...)' && \
		git pull origin $$BRANCH || echo '⚠ Git pull failed (continuing...)' && \
		echo '✓ Code updated' && \
		echo 'Building Docker images...' && \
		$(DOCKER_COMPOSE) $$PROFILE_OPT -f $$COMPOSE_FILE build --no-cache || $(DOCKER_COMPOSE) $$PROFILE_OPT -f $$COMPOSE_FILE build && \
		echo '✓ Images built' && \
		echo 'Starting services...' && \
		$(DOCKER_COMPOSE) $$PROFILE_OPT -f $$COMPOSE_FILE up -d && \
		echo '✓ Services started' && \
		echo 'Cleaning up old images...' && \
		docker image prune -f || true && \
		echo '✓ Deployment complete!' \
	" || exit 1

deploy-status: ## Check deployment status on remote server
	@. deploy.env && \
	SSH_KEY_OPT=$$([ -n "$$DEPLOY_KEY" ] && echo "-i $$DEPLOY_KEY" || echo ""); \
	SSH_PORT_OPT=$$([ -n "$$DEPLOY_PORT" ] && echo "-p $$DEPLOY_PORT" || echo ""); \
	COMPOSE_FILE=$${DEPLOY_COMPOSE_FILE:-$(DOCKER_COMPOSE).yml}; \
	ssh $$SSH_KEY_OPT $$SSH_PORT_OPT $$DEPLOY_USER@$$DEPLOY_HOST "cd $$DEPLOY_PATH && $(DOCKER_COMPOSE) -f $$COMPOSE_FILE ps"

deploy-logs: ## View logs from remote server
	@. deploy.env && \
	SSH_KEY_OPT=$$([ -n "$$DEPLOY_KEY" ] && echo "-i $$DEPLOY_KEY" || echo ""); \
	SSH_PORT_OPT=$$([ -n "$$DEPLOY_PORT" ] && echo "-p $$DEPLOY_PORT" || echo ""); \
	COMPOSE_FILE=$${DEPLOY_COMPOSE_FILE:-$(DOCKER_COMPOSE).yml}; \
	ssh $$SSH_KEY_OPT $$SSH_PORT_OPT $$DEPLOY_USER@$$DEPLOY_HOST "cd $$DEPLOY_PATH && $(DOCKER_COMPOSE) -f $$COMPOSE_FILE logs -f"

deploy-shell: ## Open shell on remote server
	@. deploy.env && \
	SSH_KEY_OPT=$$([ -n "$$DEPLOY_KEY" ] && echo "-i $$DEPLOY_KEY" || echo ""); \
	SSH_PORT_OPT=$$([ -n "$$DEPLOY_PORT" ] && echo "-p $$DEPLOY_PORT" || echo ""); \
	ssh $$SSH_KEY_OPT $$SSH_PORT_OPT $$DEPLOY_USER@$$DEPLOY_HOST "cd $$DEPLOY_PATH && bash"
