import asyncio
import concurrent.futures
import functools
import multiprocessing
import typing

from kumquat.exceptions import KumquatException


class BackgroundTask:
    thread_pool: concurrent.futures.ThreadPoolExecutor = concurrent.futures.ThreadPoolExecutor(
        max_workers=multiprocessing.cpu_count() * 5
    )

    def __init__(
        self, func: typing.Callable, *args, **kwargs,
    ):
        """
        Run task in background.
        It will be started in ThreadPoolExecutor.

        Pretty works with blocking tasks, bad works with cpu-bound tasks.
        """
        self._func = func
        self._args = args
        self._kwargs = kwargs

    async def __call__(self):
        return await self.__run()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def __run(self) -> typing.Any:
        loop = asyncio.get_running_loop()

        if asyncio.iscoroutinefunction(self._func):
            raise KumquatException(
                "function have to be synchronous,"
                " for launching async task on background"
                " use <<loop.create_task(coro)>>"
            )

        func = functools.partial(self._func, *self._args, **self._kwargs,)
        result = await loop.run_in_executor(self.thread_pool, func=func)
        return result
