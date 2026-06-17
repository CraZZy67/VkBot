from functools import wraps

from .config import Session


def with_session(func):

    @wraps(func)
    def inner(*args, **kwargs):

        if "session" in kwargs and kwargs["session"] is not None:
            return func(*args, **kwargs)

        session = Session()

        try:
            kwargs["session"] = session
            result = func(*args, **kwargs)
            session.commit()
            return result

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

    return inner