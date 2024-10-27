import json
import random
import asyncio
from aio_pika import connect, Message, IncomingMessage


class MQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue = None


    async def connect(self, uri: str):
        self.connection = await connect(uri)
        self.channel = await self.connection.channel(publisher_confirms=False)


    async def disconnect(self):
        if not self.channel.is_closed:
            await self.channel.close()
        if not self.connection.is_closed:
            await self.connection.close()


    async def is_connected(self):
        if self.connection.is_closed or self.channel.is_closed:
            return False
        return True
    

    async def _on_msg(self, msg: IncomingMessage):

        # if an exeception gets raised, message gets rejected and put beck in the queue
        async with msg.process(requeue=True):
            msg_text =  json.loads(
                msg.body.decode("utf-8")
            )

            txt = msg_text["random_id"]
            print(f"RECV: {txt}")

            # simulate random failures
            # if random.choice([True, False]):
            #     raise Exception("asdfasdf")


    async def consume(self, queue_name: str):
        self.queue = await self.channel.declare_queue(queue_name)

        await self.queue.consume(
            callback=self._on_msg,
            no_ack=False             # deliver auto ack on
        )
        
        print(f"started consuming queue {queue_name}")


    async def send_message(self, queue: str, message: dict):
        """Usage Example
        ```
        await send_message({"asdf": "asdf"})
        ```
        """
        
        async with self.channel.transaction():
            msg = Message(
                body = json.dumps(message).encode()
            )

            await self.channel.default_exchange.publish(
                message=msg,
                routing_key=queue
            )
        