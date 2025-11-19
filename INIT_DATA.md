# Инструкция по внесению тестовых данных

## Автоматическая инициализация (рекомендуется)

Тестовые данные **автоматически** вносятся при первом запуске Docker контейнеров.

### Шаги:

1. **Запустите Docker контейнеры:**
   ```bash
   make docker-up
   ```
   или
   ```bash
   docker compose up -d
   ```

2. **Дождитесь инициализации** (10-15 секунд)

3. **Проверьте логи:**
   ```bash
   docker compose logs backend | grep -E "Successfully|Created|desserts|users"
   ```
   
   Должны увидеть:
   ```
   ✓ Successfully added 20 desserts to the database.
   ✓ Created 2 test users.
   ```

4. **Проверьте данные:**
   ```bash
   docker compose exec backend python -c "from app.database import SessionLocal; from app.models import Dessert, User; db = SessionLocal(); print(f'Desserts: {db.query(Dessert).count()}'); print(f'Users: {db.query(User).count()}'); db.close()"
   ```
   
   Ожидаемый результат:
   ```
   Desserts: 20
   Users: 2
   ```

---

## Ручная инициализация

Если контейнеры уже запущены, но данные не внесены:

```bash
make docker-init-db
```

Или напрямую:

```bash
docker compose exec backend python init_db.py
```

---

## Что создается

### 20 десертов в различных категориях:

- **Cakes**: New York Cheesecake, Red Velvet, Strawberry Shortcake, Carrot Cake
- **Desserts**: Tiramisu, Panna Cotta, Chocolate Mousse, Creme Brulee
- **Pastries**: Chocolate Eclair, Macarons Assortment
- **Cookies**: Chocolate Chip Cookies
- **Tarts**: Lemon Tart, Fruit Tart
- **Pies**: Apple Pie, Pecan Pie
- **Vegan**: Vegan Brownie
- **Sugar-Free**: Sugar-Free Cake
- **Gluten-Free**: Gluten-Free Chocolate Cake
- **Ice Cream**: Ice Cream Sundae
- **Breads**: Banana Bread

### 2 тестовых пользователя:

- **Admin**: 
  - Username: `admin`
  - Password: `admin123`
  - Права: Администратор (доступ к админ-панели)

- **User**: 
  - Username: `user`
  - Password: `user123`
  - Права: Обычный пользователь

---

## Проверка работы приложения

1. **Откройте приложение:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

2. **Войдите как администратор:**
   - Username: `admin`
   - Password: `admin123`

3. **Проверьте каталог:**
   - Должно отображаться 20 десертов
   - Можно фильтровать по категориям
   - Можно искать по названию

4. **Проверьте админ-панель:**
   - Все 20 десертов должны быть видны
   - Можно редактировать и удалять
   - Можно добавлять новые

---

## Пересоздание данных

Если нужно пересоздать данные с нуля:

1. **Остановите контейнеры:**
   ```bash
   docker compose down
   ```

2. **Удалите базу данных:**
   ```bash
   rm -f backend/catalog.db backend/.db_initialized
   ```
   
   **Важно**: Если `catalog.db` является директорией (а не файлом), удалите её:
   ```bash
   rm -rf backend/catalog.db
   touch backend/catalog.db
   chmod 666 backend/catalog.db
   ```

3. **Запустите заново:**
   ```bash
   docker compose up -d
   ```

---

## Устранение проблем

### Проблема: "Database already contains data. Skipping initialization."

**Решение**: Скрипт не дублирует данные. Удалите базу данных и пересоздайте контейнеры (см. раздел "Пересоздание данных").

### Проблема: "unable to open database file"

**Решение**: 
1. Проверьте, что `backend/catalog.db` - это файл, а не директория:
   ```bash
   ls -la backend/catalog.db
   ```
2. Если это директория, удалите её и создайте файл:
   ```bash
   rm -rf backend/catalog.db
   touch backend/catalog.db
   chmod 666 backend/catalog.db
   ```
3. Перезапустите контейнеры:
   ```bash
   docker compose down && docker compose up -d
   ```

### Проблема: Контейнер перезапускается

**Решение**: Проверьте логи:
```bash
docker compose logs backend --tail 50
```

Частые причины:
- Проблемы с правами доступа к базе данных
- Отсутствует SECRET_KEY в `.env`
- Проблемы с директорией uploads

---

## Быстрый старт

```bash
# 1. Запустить контейнеры (данные внесутся автоматически)
make docker-up

# 2. Подождать 10-15 секунд

# 3. Проверить данные
docker compose exec backend python -c "from app.database import SessionLocal; from app.models import Dessert, User; db = SessionLocal(); print(f'Desserts: {db.query(Dessert).count()}'); print(f'Users: {db.query(User).count()}'); db.close()"

# 4. Открыть приложение
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs

# 5. Войти как админ
# Username: admin
# Password: admin123
```

---

## Примечания

- Скрипт проверяет наличие данных и **не создает дубликаты**
- Если данные уже есть, вы увидите: "Database already contains data. Skipping initialization."
- Для пересоздания нужно **вручную удалить** базу данных
- Файл базы данных: `backend/catalog.db` (для SQLite)
- Файл маркера инициализации: `backend/.db_initialized` (внутри контейнера)

