import asyncio
from typing import AsyncGenerator, AsyncIterator


async def _emulate_slow_operation_async(number: int) -> int:
    await asyncio.sleep(1)
    return number


async def async_number_generator(number: int) -> AsyncGenerator[int, None]:
    for number_ in range(number):
        next_next_number = await _emulate_slow_operation_async(number_)
        yield next_next_number


class AsyncIntegerGenerator:
    def __init__(self, start: int):
        self.current = start

    # It's not required to be iterable, but it's pretty common to use it.
    def __aiter__(self) -> AsyncIterator[int]:
        return self

    async def __anext__(self) -> int:
        next_number = self.current
        self.current += 1
        return next_number
