# ProCaloryAI backend

Собственный проект Каменского Андрея Игоревича, БПИ2301: сервер дневника питания.

## Запуск

Нужны Git, Docker Engine и Compose v2, свободный порт 8000. Пять команд с получением проекта:

```sh
git clone https://github.com/gonnem2/ProCaloryAI-backend.git
cd ProCaloryAI-backend
cp .env.example .env
docker compose up -d --build --wait
curl --fail http://localhost:8000/health
```

Эта инструкция относится к main после слияния PR работы 1. Для проверки до слияния клонируйте ветку командой git clone --branch lab-1 https://github.com/gonnem2/ProCaloryAI-backend.git, затем выполните оставшиеся четыре команды.

Ожидаемый ответ health: status=ok, database=ok, photos_enabled=false. [GraphQL IDE](http://localhost:8000/graphql). Миграция применяется автоматически. PostgreSQL хранит данные в именованном Docker-томе; старые папки postgres_data и minio_data не используются. Остановка без удаления данных: docker compose down.

Версии: Python 3.13.9, uv 0.9.5, PostgreSQL 17.6; Python-зависимости закреплены uv.lock. Kafka и MinIO находятся в необязательном профиле photo. Core отсутствует; PHOTOS_ENABLED=false — штатный режим для работы 1. Фотоанализ запланирован.

## Проверка основной функции

1. Вызвать register с новой почтой и получить accessToken.
2. В GraphQL Headers указать Authorization: Bearer <accessToken> и добавить через addMealLog кашу с КБЖУ 250/8/5/42.
3. Запросить meals и todayStats. В чистом дневнике — одна запись и суммы 250/8/5/42.

Запросы: [scripts/smoke.graphql](scripts/smoke.graphql). Автоматические проверки на учебной БД:

```sh
docker compose exec -T backend python -m unittest discover -s tests -v
```

10.11.2026: macOS, Linux-контейнеры с новой БД, Docker 28.5.1, Compose 2.40.0-desktop.1. Сборка, миграции и 11 API-тестов успешны; данные сохраняются после перезапуска. Проверка выполнена автоматически, другим человеком пока не проведена. [Протокол](docs/launch-check.md).

## Материалы работы 1

- [Паспорт, карта функций, практики, риски и план](docs/00-project.md)
- [Тексты issues](docs/issues.md)
- [Короткий отчёт PDF](output/pdf/Лабораторная_1_Каменский_БПИ2301.pdf)
- [Описание PR и порядок завершения](docs/lab-1-pr.md)

Документы требований и следующих этапов добавляются в соответствующих лабораторных. К концу семестра заполняются docs/01-requirements.md, docs/02-validation.md, docs/03-architecture.md, docs/04-testing.md, docs/05-deployment.md и docs/adr/.

Лицензия: [LICENSE](LICENSE), авторские права сохранены. CI и полноценный фотоанализ пока не реализованы.
