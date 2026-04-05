from domain.errors import DomainError


class UserError(DomainError):
    """Базовая ошибка агрегата пользователя."""


class UserInvalidDataError(UserError):
    """Некорректные данные пользователя."""


class UserPolicyError(UserError):
    """Ошибка политики доступа пользователей."""


class UserIdempotentError(UserError):
    """Ошибка идемпотентности пользователя."""


class UserNotFoundError(UserError):
    """Пользователь не найден."""
