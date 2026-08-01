from functools import wraps

from flask import session
from flask_restful import abort

from models import User


def login_required(fn):
    """Ensure a user is logged in (valid session) before running the view.

    On success, injects the current `User` instance as `current_user` into
    the wrapped function's kwargs.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            abort(401, errors=["Not authorized"])

        user = User.query.get(user_id)
        if not user:
            session["user_id"] = None
            abort(401, errors=["Not authorized"])

        kwargs["current_user"] = user
        return fn(*args, **kwargs)

    return wrapper
