from dataclasses import dataclass
from bcrypt import gensalt, hashpw, checkpw


@dataclass(frozen=True)
class Password:
    """Класс пароля который служит"""

    hashed_password: str

    def verify_password(self, password: str) -> bool:
        return checkpw(
            password.encode("ascii"),
            self.hashed_password.encode("ascii"),
        )

    @staticmethod
    def __hash_password(password: str) -> str:
        return hashpw(password.encode(), gensalt()).decode("ascii")

    @classmethod
    def from_raw_password(cls, raw_password: str):
        return cls(cls.__hash_password(raw_password))
