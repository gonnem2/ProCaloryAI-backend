# Проверка запуска 10 ноября 2026 года

Проверка выполнена автоматически на macOS в свежем окружении Linux-контейнеров с новой базой PostgreSQL. Репозиторий ещё не содержит опубликованных локальных исправлений.

- Docker Engine 28.5.1, Compose 2.40.0-desktop.1.
- Python 3.13.9, uv 0.9.5, PostgreSQL 17.6.
- Обычная команда запуска: docker compose up -d --build --wait.
- Сборка, начальная миграция, запуск backend и PostgreSQL успешны; оба сервиса healthy.
- GET /health: status=ok, database=ok, photos_enabled=false.
- Проверены 11 сценариев API, включая ошибки ввода, доступ к чужим данным и семидневную границу.
- Отдельная запись сохранилась после перезапуска backend; после проверки временный аккаунт удалён, его токен больше не принимается.
- В БД проверен bcrypt-хеш пароля. В логах нет вывода DSN миграции и демонстрационного ключа JWT.
- Ruff E9,F63,F7,F82: All checks passed.
- Kafka, MinIO и AI Core не запускались; фотоанализ помечен как планируемый.
- Проверка в чистом контейнерном окружении соответствует предусмотренному методичкой варианту проверки запуска; отдельный проверяющий для работы 1 не обязателен.

Вывод проверки в обычном Compose-проекте

```text
test_01_health_and_schema (test_api.DiaryAPI.test_01_health_and_schema) ... ok
test_02_login_and_refresh (test_api.DiaryAPI.test_02_login_and_refresh) ... ok
test_03_bad_credentials_and_token_type (test_api.DiaryAPI.test_03_bad_credentials_and_token_type) ... ok
test_04_duplicate_registration (test_api.DiaryAPI.test_04_duplicate_registration) ... ok
test_05_manual_diary_stats_and_ownership (test_api.DiaryAPI.test_05_manual_diary_stats_and_ownership) ... ok
test_06_validation_without_write (test_api.DiaryAPI.test_06_validation_without_write) ... ok
test_07_week_boundary_and_timezone (test_api.DiaryAPI.test_07_week_boundary_and_timezone) ... ok
test_08_goal_create_update_validation_and_progress (test_api.DiaryAPI.test_08_goal_create_update_validation_and_progress) ... ok
test_09_profile_preferences_and_privacy (test_api.DiaryAPI.test_09_profile_preferences_and_privacy) ... ok
test_10_photo_disabled_and_pagination (test_api.DiaryAPI.test_10_photo_disabled_and_pagination) ... ok
test_11_registration_validation (test_api.DiaryAPI.test_11_registration_validation) ... ok

----------------------------------------------------------------------
Ran 11 tests in 0.922s

OK
```
