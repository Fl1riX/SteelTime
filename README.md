<div align="center">

<br/>

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python_3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Aiogram](https://img.shields.io/badge/Aiogram_3-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://aiogram.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](./LICENSE)

<br/>

> **SteelTime** — сервис онлайн-записи на услуги с REST API и Telegram-ботом.  
> Никаких звонков. Никакого ожидания. Просто выбери время и запишись.

[Быстрый старт](#-быстрый-старт) • [Архитектура](#-архитектура) • [API](#-api-документация) • [Тесты](#-тесты)

</div>

---

## 📦 Стек технологий

| Слой | Технологии |
|------|-----------|
| **API** | FastAPI, Pydantic v2, SlowAPI (rate limiting) |
| **База данных** | SQLAlchemy (async), Alembic, PostgreSQL |
| **Авторизация** | JWT (access + refresh токены) |
| **Бот** | Aiogram 3, httpx |
| **Инфраструктура** | Docker, Docker Compose |
| **Тесты** | pytest, pytest-asyncio |

---

### Быстрый старт
```bash
  docker compose up --build    # собрать и запустить
  docker compose down -v       # остановить и удалить контейнеры
  docker compose logs api      # посмотреть логи конкретного сервиса
```

### Локальный запуск (без Docker)

```bash
# Установить зависимости
pip install -r requirements.txt

# Применить миграции
alembic upgrade head

# Запустить API
uvicorn main:app --reload

# Запустить бота (в отдельном терминале)
python -m src.presentation.bot.handlers.bot
```

---

После запуска доступно:
- 📄 **Swagger UI** → http://localhost:8000/docs
- 🔌 **API** → http://localhost:8000/api/v1
- 🤖 **Telegram-бот** → запущен автоматически

---

## 🏗 Архитектура

Проект построен по принципу **слоистой архитектуры**:

```
SteelTime/
├── src/
│   ├── domain/                # Бизнес-логика
│   │   ├── db/                # Модели и репозитории
│   │   └── services/          # Доменные сервисы
│   ├── infrastructure/        # Инфраструктура
│   │   └── tasks/             # Фоновые задачи
│   ├── presentation/          # Слой представления
│   │   ├── api/v1/            # REST API эндпоинты
│   │   └── bot/               # Telegram-бот
│   └── shared/
│       └── schemas/           # Pydantic DTO
├── alembic/                   # Миграции БД
├── tests/                     # Тесты
├── docker-compose.yml
└── .env.example
```

---

## 📡 API Документация

Полная интерактивная документация доступна через **Swagger UI** после запуска: `http://localhost:8000/docs`

---

## ✅ Тесты

```bash
# Запустить все тесты
pytest

# С покрытием
pytest --cov=src tests/
```

---

## ⚙️ Конфигурация

Скопируй `.env.example` в `.env` и заполни:

```env
# База данных
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/steeltime

# JWT
SECRET_KEY=               # openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Telegram
BOT_TOKEN=                # получить у @BotFather
```

---

## 📬 Контакты

**GitHub:** [@Fl1riX](https://github.com/Fl1riX)

---

<div align="center">
  <sub>Сделано с ❤️ и ☕</sub>
</div>
