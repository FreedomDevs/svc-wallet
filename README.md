
# svc-wallet

Микросервис управления кошельками пользователей. Предоставляет CRUD операции для работы с кошельками, включая пополнение, списание и получение информации о балансе.

## Быстрый старт (Docker)

### Требования
- Docker и Docker Compose

### Запуск

```bash
git clone <repo-url>
cd svc-wallet
docker compose up --build
```

API будет доступен на `http://localhost:9006`

---

## Локальная разработка (Poetry)

### Требования
- Python 3.10+
- Poetry

### Шаги
```bash
git clone <repo-url>
cd svc-wallet
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --host 0.0.0.0 --port 9006 --reload
```

## API Эндпоинты

### Основные операции с кошельками

- **POST** `/wallets` — Создать кошелёк
- **GET** `/wallets/{userId}` — Получить кошелёк
- **POST** `/wallets/{userId}/deposit` — Пополнить баланс
- **POST** `/wallets/{userId}/withdraw` — Снять средства
- **DELETE** `/wallets/{userId}` — Удалить кошелёк

### Системные эндпоинты

- **GET** `/health` — Проверка здоровья сервиса
- **GET** `/live` — Проверка живого процесса

## Примеры использования

### 1. Создание кошелька

```bash
curl -X POST http://127.0.0.1:9006/wallets \
  -H "Content-Type: application/json" \
  -H "X-Trace-Id: trace123" \
  -d '{"userId": "550e8400-e29b-41d4-a716-446655440000"}'
```

**Ответ:**
```json
{
  "data": {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "userId": "550e8400-e29b-41d4-a716-446655440000",
    "balance": 0
  },
  "message": "Wallet successfully created",
  "meta": {
    "code": "WALLET_CREATED",
    "traceId": "trace123",
    "timestamp": "2025-12-26T10:30:00Z"
  }
}
```

### 2. Пополнение кошелька

```bash
curl -X POST http://127.0.0.1:9006/wallets/550e8400-e29b-41d4-a716-446655440000/deposit \
  -H "Content-Type: application/json" \
  -d '{"amount": 1000}'
```

### 3. Снятие средств

```bash
curl -X POST http://127.0.0.1:9006/wallets/550e8400-e29b-41d4-a716-446655440000/withdraw \
  -H "Content-Type: application/json" \
  -d '{"amount": 500}'
```

### 4. Получение информации о кошельке

```bash
curl -X GET http://127.0.0.1:9006/wallets/550e8400-e29b-41d4-a716-446655440000
```

### 5. Проверка здоровья

```bash
curl -X GET http://127.0.0.1:9006/health
```


## Структура проекта

```
svc-wallet/
├── app/
│   ├── main.py           # Точка входа FastAPI
│   ├── codes.py          # Коды ошибок и успеха
│   ├── responses.py      # Форматирование ответов
│   ├── api/              # Эндпоинты (wallets, health)
│   ├── core/             # Конфиг, middleware, utils
│   ├── db/               # Модели, сессии, база
│   ├── repository/       # Репозитории
│   └── service/          # Бизнес-логика
├── alembic/              # Миграции БД
├── docker-compose.yml    # Docker конфиг
├── Dockerfile            # Dockerfile
├── pyproject.toml        # Poetry зависимости
└── README.md             # Этот файл
```

## Стандарт ответов

### Успешный ответ

```json
{
  "data": { ... },
  "message": "Описание",
  "meta": {
    "code": "WALLET_CREATED",
    "traceId": "unique-id",
    "timestamp": "2025-12-26T10:30:00Z"
  }
}
```

### Ошибка

```json
{
  "error": {
    "message": "Описание ошибки",
    "code": "WALLET_NOT_FOUND"
  },
  "meta": {
    "traceId": "unique-id",
    "timestamp": "2025-12-26T10:30:00Z"
  }
}
```

## Коды ошибок

| Код | HTTP | Описание |
|-----|------|---------|
| WALLET_CREATED | 201 | Кошелёк создан |
| WALLET_FETCHED_OK | 200 | Кошелёк получен |
| WALLET_DEPOSIT_OK | 200 | Пополнение успешно |
| WALLET_WITHDRAW_OK | 200 | Снятие успешно |
| WALLET_DELETED | 200 | Кошелёк удалён |
| USER_NOT_FOUND | 404 | Пользователь не найден |
| WALLET_NOT_FOUND | 404 | Кошелёк не найден |
| WALLET_ALREADY_EXISTS | 409 | Кошелёк уже существует |
| WALLET_INSUFFICIENT_FUNDS | 400 | Недостаточно средств |
| INVALID_REQUEST | 400 | Некорректный запрос |
| WALLET_INTERNAL_ERROR | 500 | Внутренняя ошибка |

## TraceId

Сервис поддерживает отслеживание запросов через `traceId`:

```bash
curl -H "X-Trace-Id: your-trace-id" http://127.0.0.1:9006/health
```

Если заголовок не передан, сервис генерирует новый.


## Зависимости (основные)
- fastapi
- uvicorn
- httpx
- pydantic
- sqlalchemy
- psycopg (PostgreSQL)
- alembic (dev)
