"""
Тут хендлеры событий связанных с сущностью пользователя(User)
"""

import logging
from src.domain.events.user_events import (
    UserRegistered,
    UserLoggedIn,
    UserPasswordChanged,
)

logger = logging.getLogger(__name__)


class OnUserRegistered:
    """Отправить welcome email, создать профиль и т.д."""

    async def handle(self, event: UserRegistered) -> None:
        logger.info(
            "New user registered: %s (%s) id=%s",
            event.username,
            event.email,
            event.user_id,
        )
        # await email_service.send_welcome(event.email)
        # await profile_service.create_default_profile(event.user_id)


class OnUserLoggedIn:
    async def handle(self, event: UserLoggedIn) -> None:
        logger.info("User logged in: %s id=%s", event.email, event.user_id)


class OnUserPasswordChanged:
    async def handle(self, event: UserPasswordChanged) -> None:
        logger.info("Password changed for: %s", event.email)
        # await email_service.send_security_alert(event.email)
