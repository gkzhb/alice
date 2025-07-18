import asyncio
from typing import List, Callable, Any, Optional, Dict, TypeVar, Generic
from collections.abc import Coroutine as CoroutineType

T = TypeVar("T")


class AsyncTaskQueue(Generic[T]):
    """改进版异步任务队列，基于worker模式"""

    def __init__(self, max_workers: int = 3):
        """
        初始化任务队列

        :param max_workers: worker数量，默认为3
        """
        self.max_workers = max_workers
        self.task_queue = asyncio.Queue()
        self.results_queue = asyncio.Queue()
        self.workers: List[asyncio.Task] = []
        self.task_counter = 0
        self.results_dict: Dict[int, Any] = {}
        self.expected_index = 0

    async def worker(self, worker_id: int):
        """工作协程：从队列获取并执行任务"""
        while True:
            task_id, coro = await self.task_queue.get()
            try:
                print(f"Task {task_id} started")
                result = await coro
                print(f"Task {task_id} completed")
                await self.results_queue.put((task_id, result))
            finally:
                self.task_queue.task_done()

    def add_task(self, coro: CoroutineType):
        """添加异步任务到队列"""
        self.task_queue.put_nowait((self.task_counter, coro))
        self.task_counter += 1

    async def run(
        self, post_process: Optional[Callable[[Any], Any]] = None
    ) -> List[Any]:
        """
        启动worker并运行所有任务

        :param post_process: 可选的后处理函数
        :return: 按任务添加顺序返回结果列表
        """
        # 启动worker
        self.workers = [
            asyncio.create_task(self.worker(i)) for i in range(self.max_workers)
        ]

        # 收集结果
        results = []
        collected = 0
        while collected < self.task_counter:
            task_id, result = await self.results_queue.get()
            self.results_dict[task_id] = result

            # 按顺序发送已完成的结果
            while self.expected_index in self.results_dict:
                cur_result = self.results_dict.pop(self.expected_index)
                if post_process is not None:
                    result = post_process(cur_result)
                results.append(cur_result)
                self.expected_index += 1
                collected += 1
                print(f"Progress: {collected}/{self.task_counter} tasks completed")

        # 等待所有任务完成
        await self.task_queue.join()

        # 取消worker
        for worker in self.workers:
            worker.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)

        return results

    @staticmethod
    async def execute(
        tasks: List[CoroutineType],
        max_workers: int = 3,
        post_process: Optional[Callable[[Any], Any]] = None,
    ) -> List[Any]:
        """快捷方法：一次性执行任务列表"""
        queue = AsyncTaskQueue(max_workers)
        for task in tasks:
            queue.add_task(task)
        return await queue.run(post_process)
