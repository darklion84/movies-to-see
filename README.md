# Фильмы к просмотру

Веб-сервис для ведения списка фильмов, которые вы планируете посмотреть.

## Возможности

- Поиск фильмов через TMDB API
- Добавление фильмов в список с постерами и рейтингами
- Удаление просмотренных фильмов
- Простая авторизация по паролю
- Адаптивный интерфейс для мобильных устройств

## Требования

- Python 3.11+
- Node.js 18+
- TMDB API ключ (бесплатно на [themoviedb.org](https://www.themoviedb.org/settings/api))

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone <repo-url>
   cd movies_to_see
   ```

2. Создайте файл конфигурации:
   ```bash
   cp backend/.env.example backend/.env
   ```

3. Отредактируйте `backend/.env`:
   ```
   TMDB_API_KEY=ваш_ключ_от_tmdb
   APP_PASSWORD=ваш_пароль
   SECRET_KEY=случайная_строка
   ```

## Запуск

```bash
./run.sh
```

Сервис будет доступен по адресу http://localhost:8000

## Запуск для разработки

Backend:
```bash
cd backend
pip install -r requirements.txt
python main.py
```

Frontend (в отдельном терминале):
```bash
cd frontend
npm install
npm run dev
```

## Тесты

```bash
cd backend
pytest -v
```

## Доступ извне (ngrok)

```bash
ngrok http 8000
```

Полученный URL можно использовать для доступа с телефона.

## API

| Метод  | Путь              | Описание                |
|--------|-------------------|-------------------------|
| POST   | /api/login        | Авторизация             |
| GET    | /api/movies       | Список фильмов          |
| POST   | /api/movies       | Добавить фильм          |
| DELETE | /api/movies/{id}  | Удалить фильм           |
| GET    | /api/search?q=... | Поиск в TMDB            |

## Стек технологий

- **Backend:** FastAPI, SQLAlchemy, SQLite
- **Frontend:** Vue.js 3, Vite
- **API:** TMDB (The Movie Database)
