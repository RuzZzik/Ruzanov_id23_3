# FastAPI Huffman/XOR Auth Project

## Установка

1. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```
2. Создайте файл `.env` (пример в репозитории).

3. Инициализируйте Alembic и примените миграции:
   ```
   alembic upgrade head
   ```

4. Запустите сервер:
   ```
   uvicorn main:app --reload
   ```

5. Для Celery worker (если нужно):
   ```
   celery -A app.services.celery_worker.celery worker --loglevel=info
   ```

## Основные эндпоинты
- POST `/sign-up/` — регистрация
- POST `/login/` — вход
- GET `/users/me/` — текущий пользователь
- POST `/encode` — сжать и зашифровать
- POST `/decode` — расшифровать и распаковать

## WebSocket
- ws://host/ws 