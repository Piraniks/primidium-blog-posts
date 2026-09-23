from typing import Iterator


class IntegerGenerator:
    def __init__(self, start: int):
        self.current = start

    # It's not required to be iterable, but it's pretty common to use it.
    def __iter__(self) -> Iterator[int]:
        return self

    def __next__(self) -> int:
        next_number = self.current
        self.current += 1
        return next_number
