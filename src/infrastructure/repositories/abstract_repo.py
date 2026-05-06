import abc
from typing import Generic, TypeVar, Optional, List

T = TypeVar("T")


class AbstractRepository(abc.ABC, Generic[T]):
    """
    Абстрактный обобщённый репозиторий.
    T — тип доменной сущности.
    """

    @abc.abstractmethod
    async def get(self, entity_id: int) -> Optional[T]:
        """Получить сущность по ID."""
        raise NotImplementedError

    @abc.abstractmethod
    async def add(self, entity: T) -> None:
        """Добавить новую сущность."""
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, entity: T) -> None:
        """Обновить существующую сущность."""
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, entity_id: int) -> None:
        """Удалить сущность по ID."""
        raise NotImplementedError

    @abc.abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Получить список сущностей с пагинацией."""
        raise NotImplementedError
