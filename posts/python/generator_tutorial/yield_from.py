from itertools import chain
from typing import Generator, Iterable


def _internal_generator(number: int, /) -> Generator[int, None, None]:
    yield from range(number)


def yield_from_generator(number: int, /) -> Generator[int, None, None]:
    yield from _internal_generator(number)


def yield_from_iterables(*, iterables: Iterable[Iterable[int]]) -> Generator[int, None, None]:
    for iterable in iterables:
        yield from iterable


def yield_from_iterables_using_chain(*, iterables: Iterable[Iterable[int]]) -> Generator[int, None, None]:
    yield from chain(*iterables)
