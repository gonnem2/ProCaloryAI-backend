start:
	docker compose up -d --build
stop:
	docker compose down

.PHONY: revision
revision:
	@read -p "Введите сообщение миграции: " msg;\
	export PC_MODE=migration;\
	docker compose up -d postgres;\
	PG_CONTAINER=$$(docker compose ps -q postgres); \
	until [ "$$(docker inspect -f '{{.State.Health.Status}}' $$PG_CONTAINER)" = "healthy" ]; do \
		sleep 1; \
	done; \
	uv run --active alembic revision --autogenerate -m "$$msg"

.PHONY: upgrade
upgrade:
	export PC_MODE=migration;\
	docker compose up -d postgres;\
	PG_CONTAINER=$$(docker compose ps -q postgres); \
	until [ "$$(docker inspect -f '{{.State.Health.Status}}' $$PG_CONTAINER)" = "healthy" ]; do \
		sleep 1; \
	done; \
	uv run --active alembic upgrade head
