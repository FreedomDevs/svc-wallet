# svc-wallet API Documentation

## Overview

**svc-wallet** — это внутренний CRUD-сервис для управления кошельками пользователей.

- **Название**: svc-wallet
- **Порт**: 9006
- **Версия**: 1.0.0

## Стандартный формат ответа

### Успешный ответ (200, 201)

```json
{
  "data": { ... },
  "message": "Описание операции",
  "meta": {
    "code": "WALLET_CREATED",
    "traceId": "уникальный идентификатор",
    "timestamp": "2025-12-26T10:30:00Z"
  }
}
```

### Ошибка (400, 404, 409, 500)

```json
{
  "error": {
    "message": "Описание ошибки",
    "code": "WALLET_NOT_FOUND",
    "details": [...]  // опционально
  },
  "meta": {
    "traceId": "уникальный идентификатор",
    "timestamp": "2025-12-26T10:30:00Z"
  }
}
```

## Enum коды

### Успех
- `WALLET_CREATED` (201)
- `WALLET_FETCHED_OK` (200)
- `WALLET_DEPOSIT_OK` (200)
- `WALLET_WITHDRAW_OK` (200)
- `WALLET_DELETED` (200)
- `HEALTH_OK` (200)
- `READY_OK` (200)
- `LIVE_OK` (200)

### Ошибки
- `USER_NOT_FOUND` (404)
- `WALLET_NOT_FOUND` (404)
- `WALLET_ALREADY_EXISTS` (409)
- `WALLET_INSUFFICIENT_FUNDS` (400)
- `INVALID_REQUEST` (400)
- `WALLET_INTERNAL_ERROR` (500)

---

## Эндпоинты

### 1. Создание кошелька

**POST** `/wallets`

Создаёт новый кошелёк для пользователя.

**Запрос:**
```json
{
  "userId": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Успех (201):**
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
    "traceId": "84f12ab3e7c1f5dd",
    "timestamp": "2025-12-26T10:30:00Z"
  }
}
```

**Ошибки:**
- 404 USER_NOT_FOUND — пользователь не существует
- 409 WALLET_ALREADY_EXISTS — кошелёк уже существует

---

### 2. Получение кошелька

**GET** `/wallets/{userId}`

Получает информацию о кошельке пользователя.

**Успех (200):**
```json
{
  "data": {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "userId": "550e8400-e29b-41d4-a716-446655440000",
    "balance": 1500
  },
  "message": "Wallet fetched successfully",
  "meta": {
    "code": "WALLET_FETCHED_OK",
    "traceId": "84f12ab3e7c1f5dd",
    "timestamp": "2025-12-26T10:30:00Z"
  }
}
```

**Ошибки:**
- 404 USER_NOT_FOUND — пользователь не существует
- 404 WALLET_NOT_FOUND — кошелёк не найден

---

### 3. Пополнение средств

**POST** `/wallets/{userId}/deposit`

Добавляет средства на кошелёк пользователя. Если кошелька нет, создаёт его автоматически.

**Запрос:**
```json
{
  "amount": 500
}
```

**Успех (200):**
```json
{
  "data": {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "userId": "550e8400-e29b-41d4-a716-446655440000",
    "balance": 2000
  },
  "message": "Deposit successful",
  "meta": {
    "code": "WALLET_DEPOSIT_OK",
    "traceId": "84f12ab3e7c1f5dd",
    "timestamp": "2025-12-26T10:30:00Z"
  }
}
```

**Ошибки:**
- 400 INVALID_REQUEST — некорректная сумма (≤ 0)
- 404 USER_NOT_FOUND — пользователь не существует
- 500 WALLET_INTERNAL_ERROR — ошибка при обработке

---

### 4. Списание средств

**POST** `/wallets/{userId}/withdraw`

Снимает средства с кошелька пользователя. Если кошелька нет, создаёт его автоматически.

**Запрос:**
```json
{
  "amount": 200
}
```

**Успех (200):**
```json
{
  "data": {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "userId": "550e8400-e29b-41d4-a716-446655440000",
    "balance": 1800
  },
  "message": "Withdrawal successful",
  "meta": {
    "code": "WALLET_WITHDRAW_OK",
    "traceId": "84f12ab3e7c1f5dd",
    "timestamp": "2025-12-26T10:30:00Z"
  }
}
```

**Ошибки:**
- 400 INVALID_REQUEST — некорректная сумма (≤ 0)
- 400 WALLET_INSUFFICIENT_FUNDS — недостаточно средств
- 404 USER_NOT_FOUND — пользователь не существует
- 500 WALLET_INTERNAL_ERROR — ошибка при обработке

---

### 5. Удаление кошелька

**DELETE** `/wallets/{userId}`

Удаляет кошелёк пользователя.

**Успех (200):**
```json
{
  "data": null,
  "message": "Wallet deleted successfully",
  "meta": {
    "code": "WALLET_DELETED",
    "traceId": "84f12ab3e7c1f5dd",
    "timestamp": "2025-12-26T10:30:00Z"
  }
}
```

**Ошибки:**
- 404 USER_NOT_FOUND — пользователь не существует
- 404 WALLET_NOT_FOUND — кошелёк не найден

---

## Системные эндпоинты

### 6. Health Check

**GET** `/health`

Проверяет состояние сервиса и основных зависимостей.

**Ответ (200):**
```json
{
  "data": {
    "status": "UP",
    "database": "OK",
    "dependencies": {
      "svc-users": "OK"
    }
  },
  "message": "Сервис работает",
  "meta": {
    "code": "HEALTH_OK",
    "traceId": "84f12ab3e7c1f5dd",
    "timestamp": "2025-12-26T10:30:00Z"
  }
}
```

---

### 7. Readiness

**GET** `/ready`

Проверяет, готов ли сервис принимать трафик.

**Ответ (200):**
```json
{
  "data": {
    "ready": true,
    "details": {
      "database": "connected",
      "svc-users": "connected"
    }
  },
  "message": "Сервис готов к приему трафика",
  "meta": {
    "code": "READY_OK",
    "traceId": "84f12ab3e7c1f5dd",
    "timestamp": "2025-12-26T10:30:00Z"
  }
}
```

---

### 8. Liveness

**GET** `/live`

Проверяет, жив ли процесс сервиса.

**Ответ (200):**
```json
{
  "data": {
    "alive": true
  },
  "message": "svc-wallet жив",
  "meta": {
    "code": "LIVE_OK",
    "traceId": "84f12ab3e7c1f5dd",
    "timestamp": "2025-12-26T10:30:00Z"
  }
}
```

---

### 9. Metrics

**GET** `/metrics`

Предоставляет метрики работы сервиса.

**Ответ (200):**
```json
{
  "data": {
    "requests_total": 0,
    "requests_by_method": {
      "GET": 0,
      "POST": 0,
      "DELETE": 0
    },
    "errors_total": 0
  },
  "message": "Метрики сервиса",
  "meta": {
    "code": "HEALTH_OK",
    "traceId": "84f12ab3e7c1f5dd",
    "timestamp": "2025-12-26T10:30:00Z"
  }
}
```

---

## TraceId

Все эндпоинты поддерживают передачу `traceId` через заголовок:

```
X-Trace-Id: your-trace-id-here
```

Если заголовок не передан, сервис генерирует новый `traceId` для каждого запроса.

---

## Установка и запуск

### Требования
- Python 3.8+
- pip

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Запуск

```bash
python main.py
```

Сервис запустится на `http://127.0.0.1:9006`

---

## Зависимости

- **fastapi** — REST API фреймворк
- **uvicorn** — ASGI сервер
- **httpx** — HTTP клиент для проверки внешних сервисов
- **pydantic** — валидация данных

---

## Ошибки и обработка

Все ошибки возвращаются в едином формате с полями:
- `error.message` — описание ошибки
- `error.code` — enum-код ошибки
- `meta.traceId` — идентификатор запроса для дебага
- `meta.timestamp` — время ошибки

---

## Примечания

1. У пользователя может быть только один кошелёк.
2. При пополнении или списании кошелёк создаётся автоматически, если его нет.
3. Все операции требуют проверки существования пользователя через svc-users.
4. Баланс хранится как целое число.
5. Сервис использует SQLite для хранения данных.
