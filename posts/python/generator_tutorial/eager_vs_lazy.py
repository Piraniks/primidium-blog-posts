import time
from typing import Generator, Iterable


def _emulate_slow_operation(number: int) -> int:
    time.sleep(1)
    return number


def lazy_number_generator(number: int) -> Iterable[int]:
    result = []
    for number_ in range(number):
        result.append(_emulate_slow_operation(number_))

    return result


def eager_number_generator(number: int) -> Generator[int, None, None]:
    for number_ in range(number):
        yield number_
