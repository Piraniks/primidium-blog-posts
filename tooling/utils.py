from contextlib import contextmanager
from decimal import Decimal
from functools import wraps
from time import monotonic
from typing import IO, Callable, Generator


@contextmanager
def timer(
    *, logger: IO, name: str = 'timer context manager', display_threshold: Decimal = Decimal(0.01)
) -> Generator[None, None, None]:
    before = monotonic()
    yield
    after = monotonic()

    time_elapsed = after - before
    if time_elapsed > display_threshold:
        logger.write(f'Elapsed time of {name}: {time_elapsed}')


def timed[**P, T](callable_: Callable[P, T], /) -> Callable[P, T]:
    @wraps(wrapped=callable_)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        logger = kwargs.pop('logger')
        callable_name = getattr(callable_, '__name__', 'anonymous_function')
        with timer(name=callable_name, logger=logger):
            result = callable_(*args, **kwargs, logger=logger)

        return result

    return wrapper
