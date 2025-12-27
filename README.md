# svc-wallet

Микросервис управления кошельками пользователей. Предоставляет CRUD операции для работы с кошельками, включая пополнение, списание и получение информации о балансе.

## Особенности

- ✅ REST API на FastAPI
- ✅ Полная поддержка API Guidelines (стандарт ответов/ошибок)
- ✅ TraceId для отслеживания запросов
- ✅ Проверка существования пользователей через svc-users
- ✅ Автоматическое создание кошелька при необходимости
- ✅ Health, Ready, Live, Metrics эндпоинты
- ✅ SQLite база данных

## Установка

### Требования
- Python 3.8 или выше
- pip

### Шаги

1. **Клонировать репозиторий**
```bash
cd d:\Projects\svc-wallet
```

2. **Создать виртуальное окружение**

На Linux/Mac:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

На Windows:
```bash
python3 -m venv .venv
.venv\Scripts\activate.bat
```

3. **Установить зависимости**
```bash
pip install -r requirements.txt
```

4. **Запустить сервис**
```bash
python main.py
```

Сервис запустится на `http://127.0.0.1:9006`

## API Эндпоинты

### Основные операции с кошельками

- **POST** `/wallets` — Создать кошелёк
- **GET** `/wallets/{userId}` — Получить кошелёк
- **POST** `/wallets/{userId}/deposit` — Пополнить баланс
- **POST** `/wallets/{userId}/withdraw` — Снять средства
- **DELETE** `/wallets/{userId}` — Удалить кошелёк

### Системные эндпоинты

- **GET** `/health` — Проверка здоровья сервиса
- **GET** `/ready` — Проверка готовности к трафику
- **GET** `/live` — Проверка живого процесса
- **GET** `/metrics` — Метрики сервиса

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
├── main.py                 # Entry point приложения
├── codes.py               # Enum коды ошибок и успеха
├── responses.py           # Форматирование ответов
├── database.py            # Работа с БД (SQLite)
├── utils.py               # Утилиты (TraceId, timestamp)
├── requirements.txt       # Python зависимости
├── docker-compose.yml     # Docker конфигурация
├── routes/
│   ├── __init__.py       # Подключение роутеров
│   ├── health.py         # Системные эндпоинты
│   └── wallets.py        # CRUD эндпоинты для кошельков
├── README.md             # Этот файл
└── API.md                # Полная документация API
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

## Зависимости

- **fastapi** (^0.125.0) — веб-фреймворк
- **uvicorn** (^0.38.0) — ASGI сервер
- **httpx** (^0.27.0) — HTTP клиент
- **pydantic** (^2.8.0) — валидация данных

## Разработка

### Для добавления нового эндпоинта

1. Добавить код в `codes.py`
2. Создать функцию в `routes/wallets.py`
3. Использовать `success_response()` и `error_response()`

### Для изменения БД

1. Отредактировать функции в `database.py`
2. При необходимости пересоздать БД

## Docker

```bash
docker-compose up
```

## Контакты

Для вопросов обратитесь к разработчику микросервиса.
