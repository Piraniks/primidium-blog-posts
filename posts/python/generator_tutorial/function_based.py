from typing import Any, Generator


def generator_yielding_what_it_is_given(number: Any) -> Generator[Any, None, None]:
    yield number


def generator_producing_infinite_integers() -> Generator[int, None, None]:
    number = 0
    while True:
        yield number
        number += 1


def generator_with_multiple_yields() -> Generator[str, None, None]:
    yield 'first'
    yield 'second'


def generator_with_data_memory(initial_value: int) -> Generator[int, int, None]:
    generator_data = initial_value
    while True:
        generator_data = yield generator_data


def generator_returning_data() -> Generator[int, None, str]:
    yield 1

    # This value will be returned as the StopIteration exception's value attribute.
    return 'Done'
