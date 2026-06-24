import os

limiter = None


def setup_rate_limiter(app):
    global limiter
    if os.getenv("DISABLE_RATE_LIMIT") != "true":
        from slowapi import Limiter, _rate_limit_exceeded_handler
        from slowapi.util import get_remote_address
        limiter = Limiter(key_func=get_remote_address)
        app.state.limiter = limiter
        app.add_exception_handler(429, _rate_limit_exceeded_handler)


def limit(rate: str):
    if limiter is not None:
        return limiter.limit(rate)
    return lambda func: func
