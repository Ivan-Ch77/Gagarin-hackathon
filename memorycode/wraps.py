from functools import wraps
import logging

class AuthenticationError(Exception):
    """Исключение, поднимаемое при отсутствии токена доступа."""
    pass


def require_auth(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if not self.access_token:
            logging.error("Токен доступа не установлен.")
            raise AuthenticationError("Токен доступа не установлен.")
        return await func(self, *args, **kwargs)
    return wrapper
