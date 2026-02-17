import functools

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods


def debug(func):
    """Print the function signature and return value"""

    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        try:
            is_callable = func.__call__
        except AttributeError:
            is_callable = None

        if is_callable:
            print(f"Calling {func.__name__}({signature})")  # noqa: T201
            value = func(*args, **kwargs)
            print(f"{func.__name__}() returned {value!r}")  # noqa: T201
            return value

        print(f"Debugged object {func!r} cannot be called")  # noqa: T201
        return func

    return wrapper_debug


def require(methods=("GET", "POST"), *, login=True):
    """View decorator to require a set of HTTP methods and login
    `login` is required by default"""

    # TODO: handle HTMX requests, they shouldn't redirect to login
    def wrapper(func):
        wrapped = func
        if methods is not None:
            wrapped = require_http_methods(methods)(func)
        if login:
            wrapped = login_required(func)
        return wrapped

    return wrapper
