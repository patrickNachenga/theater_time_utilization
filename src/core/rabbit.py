import asyncio
import json
from typing import List

import aio_pika
from aio_pika import connect_robust
from aio_pika.abc import AbstractRobustConnection
from aio_pika.pool import Pool

from src.core.config import settings, QUEUES


class RabbitMQ:
    def __init__(self, log_incoming_message):
        """
            Initialize RabbitMQ Connection
        :param :
        """

        loop = asyncio.get_event_loop()
        self.log_incoming_message = log_incoming_message

        async def get_connection() -> AbstractRobustConnection:
            return await connect_robust(
                host=settings.RABBIT_HOST,
                port=settings.RABBIT_PORT,
                login=settings.RABBIT_USERNAME,
                password=settings.RABBIT_PASSWORD,
                loop=loop
            )

        self.connection_pool: Pool = Pool(get_connection, max_size=2, loop=loop)

        async def get_channel() -> aio_pika.Channel:
            async with self.connection_pool.acquire() as connection:
                return await connection.channel()

        self.channel_pool: Pool = Pool(get_channel, max_size=10, loop=loop)

        self.log_incoming_message('Rabbitmq connection initialized')

    async def setup(self):
        for queue in QUEUES:
            try:
                self.log_incoming_message('Declaring queue: ' + queue['name'])
                await self.declare_exchange(queue["exchange"], queue["type"])
                await self.declare_queue(name=queue['name'], exchange=queue['exchange'],
                                         routing_key=queue['routing_key'])
            except Exception as e:
                print(e)
                self.log_incoming_message('Error: ' + str(e))

    async def declare_queue(self, name: str, exchange, routing_key):
        async with self.channel_pool.acquire() as channel:  # type: aio_pika.Channel
            await channel.set_qos(10)
            queue = await channel.declare_queue(
                name, durable=True, auto_delete=False,
            )
            await queue.bind(exchange, routing_key)

    async def declare_exchange(self, name: str, exchange_type: str):
        async with self.channel_pool.acquire() as channel:  # type: aio_pika.Channel
            await channel.set_qos(10)
            await channel.declare_exchange(name=name, type=exchange_type)

    async def publish(self, exchange, routing_key, body):
        async with self.channel_pool.acquire() as channel:  # type: aio_pika.Channel
            await channel.set_qos(10)
            exchange_obj = await channel.get_exchange(name=exchange)
            await exchange_obj.publish(
                aio_pika.Message(
                    body=body.encode()
                ),
                routing_key=routing_key
            )

    async def consume(self, queues: List[str]):
        """Setup message listener with the current running loop"""
        async with self.channel_pool.acquire() as channel:  # type: aio_pika.Channel
            await channel.set_qos(10)
            for queue in queues:
                queue_obj = await channel.get_queue(queue)
                await queue_obj.consume(self.process_incoming_message, no_ack=False)
                self.log_incoming_message(f'Established {queue} async listener')

    @staticmethod
    async def process_incoming_message(message: aio_pika.abc.AbstractIncomingMessage):
        """Processing incoming message from RabbitMQ"""
        try:
            if message.routing_key == 'sua-esb-permission-routing-key':
                permissions = json.loads(message.body.decode())
            else:
                pass
        except Exception as e:
            print(e)
