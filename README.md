# LMS Platform

REST API для системы управления обучением (Learning Management System) с ролевой моделью, JWT-аутентификацией, подписками и фоновыми задачами.

## Стек технологий

| Категория | Технология |
|-----------|------------|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| База данных | PostgreSQL |
| Драйвер БД | asyncpg |
| Валидация | Pydantic v2 |
| Аутентификация | JWT (access + refresh tokens) |
| Миграции | Alembic |
| Тестирование | pytest + pytest-asyncio + pytest-cov |
| Фоновые задачи | APScheduler + BackgroundTasks |
| Контейнеризация | Docker + Docker Compose |

## Архитектура проекта

```
lms-project/
├── app/
│   ├── api/              # Роутеры (auth, courses, subscriptions)
│   ├── crud/             # Бизнес-логика
│   ├── models/           # SQLAlchemy ORM-модели
│   ├── schemas/          # Pydantic-схемы
│   ├── exceptions/       # Кастомные исключения и хендлеры
│   ├── dependencies/     # Зависимости (auth, БД)
│   ├── utils/            # Security, email
│   └── tasks/            # Фоновый scheduler
├── tests/                # Pytest-тесты
├── migrations/           # Alembic-миграции
├── Dockerfile
├── docker-compose.yaml
├── docker-entrypoint.sh
├── init.sql              # Инициализация тестовой БД
├── requirements.txt
├── alembic.ini
└── README.md
```

## Функционал

- **Аутентификация**: регистрация, вход, refresh-токен, выход
- **Ролевая модель**: `teacher` (создаёт курсы) / `student` (подписывается на курсы)
- **Курсы**: CRUD с проверкой прав доступа (только владелец может редактировать/удалять)
- **Подписки**: покупка курса, отмена, проверка активности
- **Soft delete**: пользователи помечаются `is_active=False`, а не удаляются физически
- **Фоновые задачи**: автоматическая деактивация истёкших подписок (APScheduler)
- **Email-уведомления**: отправка при подписке (BackgroundTasks)
- **Пагинация**: списки курсов и подписок с `skip` / `limit`
- **Централизованная обработка ошибок**: кастомные исключения с единым форматом ответа

## Быстрый старт (Docker)

```bash
# 1. Клонируй репозиторий
git clone https://github.com/El1xirq/lms-project.git
cd lms-project

# 2. Создай .env из шаблона
cp .env.example .env

# 3. Запусти проект. Перед запуском автоматически применятся миграции.
docker compose up --build
```

Приложение будет доступно по адресу: `http://localhost:8000`

Документация API (Swagger UI): `http://localhost:8000/docs`

После перехода со старой версии, где таблицы создавались через `create_all`,
для чистого локального запуска один раз выполни:

```bash
docker compose down -v
docker compose up --build
```

Команда `down -v` удаляет локальный том PostgreSQL вместе с данными.

## Локальный запуск (без Docker)

### Требования

- Python 3.12+
- PostgreSQL 14+

### Установка

```bash
# 1. Клонируй репозиторий
git clone https://github.com/El1xirq/lms-project.git
cd lms-project

# 2. Создай виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 3. Установи зависимости
pip install -r requirements.txt

# 4. Создай базы данных
# Основная: lms_db
# Тестовая: lms_test

# 5. Примени миграции
alembic upgrade head

# 6. Запусти сервер
uvicorn app.main:app --reload
```

Приложение больше не создаёт таблицы через `Base.metadata.create_all()` при каждом
запуске. Схема базы управляется Alembic. Для Docker миграции применяются
автоматически через `docker-entrypoint.sh`.

## Тестирование

```bash
# Запуск всех тестов
pytest

# С покрытием кода
pytest --cov=app --cov-report=term-missing

# HTML-отчёт о покрытии
pytest --cov=app --cov-report=html
```

### Тестовое покрытие

- **Auth**: регистрация, вход, refresh, logout, невалидные данные
- **Courses**: создание, получение, обновление, удаление, права доступа
- **Subscriptions**: подписка, дубли, отмена, чужие подписки

## Переменные окружения

Создай файл `.env` на основе `.env.example`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:change-me@localhost:5432/lms_db
SYNC_DATABASE_URL=postgresql+psycopg2://postgres:change-me@localhost:5432/lms_db
TEST_DATABASE_URL=postgresql+asyncpg://postgres:change-me@localhost:5432/lms_test

SECRET_KEY=сгенерируй-новый-секрет
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
DEBUG=True
```

**Важно**: `SECRET_KEY` должен быть уникальным и храниться в секрете. Никогда не коммить файл `.env`.

Если старый `.env` уже попадал в GitHub, одного удаления файла недостаточно:
нужно заменить `SECRET_KEY` и пароль базы, потому что старые значения уже нельзя
считать секретными.

## API Endpoints

### Auth

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/auth/register` | Регистрация |
| POST | `/auth/login` | Вход (OAuth2) |
| POST | `/auth/refresh` | Обновление access-токена |
| POST | `/auth/logout` | Выход |

### Courses

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/courses/` | Список курсов (пагинация) |
| GET | `/courses/{id}` | Детали курса |
| POST | `/courses/` | Создание курса (teacher) |
| PATCH | `/courses/{id}` | Обновление курса (владелец) |
| DELETE | `/courses/{id}` | Удаление курса (владелец) |

### Subscriptions

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/subscriptions/?course_id={id}` | Подписка на курс (student) |
| GET | `/subscriptions/my` | Мои подписки |
| GET | `/subscriptions/my/active` | Мои активные подписки |
| DELETE | `/subscriptions/{id}` | Отмена подписки |

## Лицензия

MIT
