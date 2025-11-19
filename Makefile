.PHONY: help install install-backend install-frontend init-db run run-backend run-frontend clean clean-backend clean-frontend restart test

# Переменные
PYTHON := python3
PIP := pip
NPM := npm
VENV := backend/venv
VENV_BIN := $(VENV)/bin
BACKEND_DIR := backend
FRONTEND_DIR := frontend

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

