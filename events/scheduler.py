"""
Base worker.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""


import asyncio
import logging
import time
from concurrent.futures import CancelledError
from typing import Dict

import msgpack
from aiokafka import AIOKafkaConsumer

from config import Config as C

log = logging.getLogger(__name__)

_listeners: Dict = {}


def add(*routing_keys: str):
    """Decorator, adds the decorated function as a callback for the given routing key.

    :args: list of routing keys.
    """
    def decorator(func):
        for routing_key in routing_keys:
            if routing_key in _listeners:
                _listeners[routing_key] = _listeners[routing_key] + (func,)
            else:
                _listeners[routing_key] = (func,)
        return func

    return decorator


async def worker(queue, app):
    """Work on tasks."""
    try:
        while True:
            now = time.time()

            # wait for an item from the producer
            task = await queue.get()
            func = task[2]
            log.info(f"Executing task `{task[2].__name__}`")
            try:
                await func(task[3], task[4], app)
            except CancelledError:
                log.warning(f"Task `{task[2].__name__}` cancelled.")
                raise
            except Exception as err:
                log.exception(f"Task `{task[2].__name__}` failed.")
            else:
                log.info(f"Task `{task[2].__name__}` completed in {time.time() - now}.")
            finally:
                queue.task_done()
                log.info(f"Task `{task[2].__name__}` removed.")
    except CancelledError:
        log.warning("Consumer cancelled.")


async def main(app):
    """Launch the task manager."""
    try:
        task_index = 0

        tasks_queue = asyncio.PriorityQueue(maxsize=5)
        worker_task = asyncio.ensure_future(worker(tasks_queue, app))

        log.info("Loading listeners....")
        for binding_key, funcs in _listeners.items():
            for func in funcs:
                log.info(f"Function `{func.__name__}` listen on `{binding_key}`")

        # Perform connection
        consumer = AIOKafkaConsumer(
            *_listeners.keys(), loop=app.loop, bootstrap_servers=C.KAFKA_URI)

        # Start listening the queue with name 'task_queue'
        await consumer.start()
        log.info(f"Scheduler Kafka consumer started.")

        async for message in consumer:

            log.info(f"Received a new event: {message.topic}")
            # selecter will yield functions to run
            for func in _listeners.get(message.topic, []):
                body = msgpack.unpackb(message.value, encoding='utf-8')
                priority = body.get("priority", 1)
                entry = (priority, task_index, func, message.topic, body)
                log.info(f"Create a new task: `{func.__name__}` - priority {priority} - index {task_index}")
                await tasks_queue.put(entry)
                task_index += 1

    except CancelledError:
        log.warning("Closing background task manager.....")
        await consumer.stop()
        log.warning("Kafka connector stopped.")
        log.warning("Closing tasks....")
        worker_task.cancel()
        await tasks_queue.join()
