.PHONY: help install install-backend install-frontend init-db run-backend run-frontend run-all-bg stop restart setup clean clean-backend clean-frontend clean-all logs-backend logs-frontend status docker-up docker-down docker-build docker-logs docker-init-db docker-shell-backend docker-shell-frontend docker-restart deploy deploy-check deploy-remote deploy-status deploy-logs deploy-shell

# Переменные
PYTHON := python3
NPM := npm
VENV := backend/venv
VENV_BIN := $(VENV)/bin
BACKEND_DIR := backend
FRONTEND_DIR := frontend
DOCKER_COMPOSE := $(shell command -v docker-compose >/dev/null 2>&1 && echo docker-compose || echo docker compose)

# Цвета для вывода
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help: ## Показать справку по командам
	@echo "$(GREEN)Доступные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

# ============================================================================
# Установка зависимостей
# ============================================================================

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

# ============================================================================
# Инициализация
# ============================================================================

init-db: ## Инициализировать базу данных с тестовыми данными
	@echo "$(GREEN)Инициализация базы данных...$(NC)"
	@$(VENV_BIN)/python $(BACKEND_DIR)/init_db.py
	@echo "$(GREEN)✓ База данных инициализирована$(NC)"

setup: install init-db ## Полная настройка проекта (установка + инициализация БД)
	@echo "$(GREEN)✓ Проект готов к запуску!$(NC)"
	@echo "$(YELLOW)Запустите:$(NC) make run-all-bg"

# ============================================================================
# Запуск сервисов (локально)
# ============================================================================

run-backend: install-backend ## Запустить только бэкенд
	@echo "$(GREEN)Запуск бэкенд-сервера...$(NC)"
	@if [ ! -f "$(VENV_BIN)/uvicorn" ] && ! $(VENV_BIN)/python -m uvicorn --version >/dev/null 2>&1; then \
		echo "$(YELLOW)⚠ uvicorn не найден. Устанавливаю зависимости...$(NC)"; \
		$(MAKE) install-backend; \
	fi
	@PROJECT_ROOT=$$(pwd); \
	cd $(BACKEND_DIR) && if [ -f "$$PROJECT_ROOT/$(VENV_BIN)/uvicorn" ]; then \
		$$PROJECT_ROOT/$(VENV_BIN)/uvicorn main:app --reload --host 0.0.0.0 --port 8000; \
	else \
		$$PROJECT_ROOT/$(VENV_BIN)/python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000; \
	fi

run-frontend: install-frontend ## Запустить только фронтенд
	@echo "$(GREEN)Запуск фронтенд-сервера...$(NC)"
	@if [ ! -d "$(FRONTEND_DIR)/node_modules" ]; then \
		echo "$(YELLOW)⚠ node_modules не найдены. Устанавливаю зависимости...$(NC)"; \
		$(MAKE) install-frontend; \
	fi
	@cd $(FRONTEND_DIR) && $(NPM) run dev

run-backend-bg: install-backend ## Запустить бэкенд в фоновом режиме
	@echo "$(GREEN)Запуск бэкенд-сервера в фоне...$(NC)"
	@if [ ! -f "$(VENV_BIN)/uvicorn" ] && ! $(VENV_BIN)/python -m uvicorn --version >/dev/null 2>&1; then \
		echo "$(YELLOW)⚠ uvicorn не найден. Устанавливаю зависимости...$(NC)"; \
		$(MAKE) install-backend; \
	fi
	@PROJECT_ROOT=$$(pwd); \
	cd $(BACKEND_DIR) && if [ -f "$$PROJECT_ROOT/$(VENV_BIN)/uvicorn" ]; then \
		nohup $$PROJECT_ROOT/$(VENV_BIN)/uvicorn main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 & echo $$! > backend.pid; \
	else \
		nohup $$PROJECT_ROOT/$(VENV_BIN)/python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 & echo $$! > backend.pid; \
	fi
	@echo "$(GREEN)✓ Бэкенд запущен (PID: $$(cat $(BACKEND_DIR)/backend.pid))$(NC)"
	@echo "Логи: tail -f $(BACKEND_DIR)/backend.log"

run-frontend-bg: install-frontend ## Запустить фронтенд в фоновом режиме
	@echo "$(GREEN)Запуск фронтенд-сервера в фоне...$(NC)"
	@if [ ! -d "$(FRONTEND_DIR)/node_modules" ]; then \
		echo "$(YELLOW)⚠ node_modules не найдены. Устанавливаю зависимости...$(NC)"; \
		$(MAKE) install-frontend; \
	fi
	@cd $(FRONTEND_DIR) && nohup $(NPM) run dev > frontend.log 2>&1 & echo $$! > frontend.pid
	@echo "$(GREEN)✓ Фронтенд запущен (PID: $$(cat $(FRONTEND_DIR)/frontend.pid))$(NC)"
	@echo "Логи: tail -f $(FRONTEND_DIR)/frontend.log"

run-all-bg: run-backend-bg run-frontend-bg ## Запустить всё в фоновом режиме
	@echo "$(GREEN)✓ Все сервисы запущены в фоне$(NC)"
	@echo "$(YELLOW)Бэкенд:$(NC) http://localhost:8000"
	@echo "$(YELLOW)Фронтенд:$(NC) http://localhost:3000"
	@echo "$(YELLOW)API Docs:$(NC) http://localhost:8000/docs"

# ============================================================================
# Управление сервисами
# ============================================================================

stop: ## Остановить все фоновые процессы
	@echo "$(GREEN)Остановка сервисов...$(NC)"
	@if [ -f "$(BACKEND_DIR)/backend.pid" ]; then \
		PID=$$(cat $(BACKEND_DIR)/backend.pid 2>/dev/null); \
		if [ -n "$$PID" ] && ps -p $$PID > /dev/null 2>&1; then \
			# Проверяем, что это действительно наш процесс (uvicorn или python)
			if ps -p $$PID -o comm= 2>/dev/null | grep -qE "uvicorn|python"; then \
				kill $$PID 2>/dev/null || true; \
				echo "$(GREEN)✓ Бэкенд остановлен$(NC)"; \
			else \
				echo "$(YELLOW)⚠ PID $$PID не является процессом бэкенда$(NC)"; \
			fi; \
		fi; \
		rm -f $(BACKEND_DIR)/backend.pid; \
	fi
	@if [ -f "$(FRONTEND_DIR)/frontend.pid" ]; then \
		PID=$$(cat $(FRONTEND_DIR)/frontend.pid 2>/dev/null); \
		if [ -n "$$PID" ] && ps -p $$PID > /dev/null 2>&1; then \
			# Проверяем, что это действительно наш процесс (node или npm)
			if ps -p $$PID -o comm= 2>/dev/null | grep -qE "node|npm"; then \
				kill $$PID 2>/dev/null || true; \
				echo "$(GREEN)✓ Фронтенд остановлен$(NC)"; \
			else \
				echo "$(YELLOW)⚠ PID $$PID не является процессом фронтенда$(NC)"; \
			fi; \
		fi; \
		rm -f $(FRONTEND_DIR)/frontend.pid; \
	fi

restart: stop run-all-bg ## Перезапустить все сервисы

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

logs-backend: ## Показать логи бэкенда
	@tail -f $(BACKEND_DIR)/backend.log 2>/dev/null || echo "$(YELLOW)Логи не найдены. Запустите: make run-backend-bg$(NC)"

logs-frontend: ## Показать логи фронтенда
	@tail -f $(FRONTEND_DIR)/frontend.log 2>/dev/null || echo "$(YELLOW)Логи не найдены. Запустите: make run-frontend-bg$(NC)"

# ============================================================================
# Очистка
# ============================================================================

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

# ============================================================================
# Docker команды
# ============================================================================

docker-up: ## Запустить все сервисы в Docker
	@echo "$(GREEN)Запуск через скрипт start-docker.sh...$(NC)"
	@if [ ! -f "$(BACKEND_DIR)/.env" ]; then \
		echo "$(YELLOW)Создание backend/.env из env.example...$(NC)"; \
		cp $(BACKEND_DIR)/env.example $(BACKEND_DIR)/.env; \
		echo "$(YELLOW)⚠ ВАЖНО: Отредактируйте backend/.env и установите SECRET_KEY!$(NC)"; \
	fi
	@./start-docker.sh || { \
		echo "$(YELLOW)⚠ Ошибка при запуске. Попробуйте вручную:$(NC)"; \
		echo "  ./start-docker.sh"; \
		echo "  или"; \
		echo "  docker compose up -d"; \
		exit 1; \
	}

docker-up-prod: ## Запустить с PostgreSQL (production)
	@echo "$(GREEN)Запуск Docker Compose с PostgreSQL...$(NC)"
	@if [ ! -f "$(BACKEND_DIR)/.env" ]; then \
		echo "$(YELLOW)Создание backend/.env из env.example...$(NC)"; \
		cp $(BACKEND_DIR)/env.example $(BACKEND_DIR)/.env; \
		echo "$(YELLOW)⚠ ВАЖНО: Отредактируйте backend/.env!$(NC)"; \
	fi
	@$(DOCKER_COMPOSE) --profile production up -d
	@echo "$(GREEN)✓ Сервисы запущены с PostgreSQL$(NC)"

docker-down: ## Остановить все Docker сервисы
	@echo "$(GREEN)Остановка Docker Compose...$(NC)"
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ Сервисы остановлены$(NC)"

docker-build: ## Пересобрать Docker контейнеры
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

# ============================================================================
# Deployment команды
# ============================================================================

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
	COMPOSE_FILE=$${DEPLOY_COMPOSE_FILE:-docker-compose.yml}; \
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
		docker-compose $$PROFILE_OPT -f $$COMPOSE_FILE build --no-cache || docker compose $$PROFILE_OPT -f $$COMPOSE_FILE build || docker-compose $$PROFILE_OPT -f $$COMPOSE_FILE build && \
		echo '✓ Images built' && \
		echo 'Starting services...' && \
		(docker-compose $$PROFILE_OPT -f $$COMPOSE_FILE up -d || docker compose $$PROFILE_OPT -f $$COMPOSE_FILE up -d) && \
		echo '✓ Services started' && \
		echo 'Cleaning up old images...' && \
		docker image prune -f || true && \
		echo '✓ Deployment complete!' \
	" || exit 1

deploy-status: ## Check deployment status on remote server
	@. deploy.env && \
	SSH_KEY_OPT=$$([ -n "$$DEPLOY_KEY" ] && echo "-i $$DEPLOY_KEY" || echo ""); \
	SSH_PORT_OPT=$$([ -n "$$DEPLOY_PORT" ] && echo "-p $$DEPLOY_PORT" || echo ""); \
	COMPOSE_FILE=$${DEPLOY_COMPOSE_FILE:-docker-compose.yml}; \
	ssh $$SSH_KEY_OPT $$SSH_PORT_OPT $$DEPLOY_USER@$$DEPLOY_HOST "cd $$DEPLOY_PATH && (docker-compose -f $$COMPOSE_FILE ps || docker compose -f $$COMPOSE_FILE ps)"

deploy-logs: ## View logs from remote server
	@. deploy.env && \
	SSH_KEY_OPT=$$([ -n "$$DEPLOY_KEY" ] && echo "-i $$DEPLOY_KEY" || echo ""); \
	SSH_PORT_OPT=$$([ -n "$$DEPLOY_PORT" ] && echo "-p $$DEPLOY_PORT" || echo ""); \
	COMPOSE_FILE=$${DEPLOY_COMPOSE_FILE:-docker-compose.yml}; \
	ssh $$SSH_KEY_OPT $$SSH_PORT_OPT $$DEPLOY_USER@$$DEPLOY_HOST "cd $$DEPLOY_PATH && (docker-compose -f $$COMPOSE_FILE logs -f || docker compose -f $$COMPOSE_FILE logs -f)"

deploy-shell: ## Open shell on remote server
	@. deploy.env && \
	SSH_KEY_OPT=$$([ -n "$$DEPLOY_KEY" ] && echo "-i $$DEPLOY_KEY" || echo ""); \
	SSH_PORT_OPT=$$([ -n "$$DEPLOY_PORT" ] && echo "-p $$DEPLOY_PORT" || echo ""); \
	ssh $$SSH_KEY_OPT $$SSH_PORT_OPT $$DEPLOY_USER@$$DEPLOY_HOST "cd $$DEPLOY_PATH && bash"
