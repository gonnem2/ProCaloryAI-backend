# ProCaloryAI

Сервер личного дневника питания. В первой лабораторной работают регистрация, вход, ручное добавление еды, дневник, статистика и цель снижения веса. Анализ фотографий через внешний AI Core запланирован на следующие этапы.

## Стек и версии инструментов

| Инструмент | Версия |
| --- | --- |
| Python | 3.13.9 |
| uv | 0.9.5 |
| PostgreSQL | 17.6 |
| Docker Engine | Проверено на 28.5.1 |
| Docker Compose | Проверено на 2.40.0-desktop.1 |
| API | FastAPI и Strawberry GraphQL |

Версии библиотек зафиксированы в uv.lock. Python и uv устанавливаются внутри Docker-образа.

## Запуск

Нужны Git, Docker и Docker Compose. Порт 8000 должен быть свободен.

```sh
git clone --branch lab-1 https://github.com/gonnem2/ProCaloryAI-backend.git
cd ProCaloryAI-backend
cp .env.example .env
docker compose up -d --build --wait
curl --fail http://localhost:8000/health
```

Откройте [GraphQL IDE](http://localhost:8000/graphql). Backend и PostgreSQL запускаются автоматически, миграция применяется при старте. Kafka, MinIO и AI Core для Lab 1 не требуются. PHOTOS_ENABLED=false — обычный режим запуска.

### Проверка работоспособности

1. Выполните register с новой почтой, сохраните accessToken.
2. В Headers укажите Authorization: Bearer <accessToken>. Добавьте приём пищи через addMealLog.
3. Выполните meals и todayStats: новая запись должна появиться в дневнике и статистике.

Готовые запросы: [scripts/smoke.graphql](scripts/smoke.graphql).

Автоматический smoke после запуска:

```sh
docker compose exec -T backend python - < scripts/smoke.py
```

Дополнительные API-тесты:

```sh
docker compose exec -T backend python -m unittest discover -s tests -v
```

План показа преподавателю: [docs/demo-plan.md](docs/demo-plan.md).

## Скриншоты

| Что показано | Скриншот |
| --- | --- |
| Регистрация | [01-register.png](docs/screenshots/01-register.png) |
| Добавление питания | [02-add-meal.png](docs/screenshots/02-add-meal.png) |
| Дневник и статистика | [03-diary.png](docs/screenshots/03-diary.png) |
| Профиль и настройки | [04-profile.png](docs/screenshots/04-profile.png) |

Это экраны GraphQL IDE работающего backend. Отдельный пользовательский интерфейс в проект не входит.

## Протокол проверки запуска

| Дата | Окружение | Кто проверял | Результат |
| --- | --- | --- | --- |
| 10.11.2026 | macOS, чистые Linux-контейнеры, новая БД | Автоматизированная проверка | Сборка, миграция, 11 API-тестов и сохранение данных после перезапуска — OK |

Данные PostgreSQL сохраняются в именованном Docker-томе. Остановка с сохранением данных: docker compose down.

## Структура

Паспорт, карта функций, риски и план семестра: [docs/00-project.md](docs/00-project.md). Документы для следующих работ пока содержат заготовки.

## Лицензия

Авторские права сохранены, см. [LICENSE](LICENSE).
