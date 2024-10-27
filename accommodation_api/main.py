import os
import string
import random
from fastapi import FastAPI
from accommodation_api.core.mq import MQClient
from contextlib import asynccontextmanager

mq_uri = os.environ.get("RABBIT_URI", "amqp://guest:guest@mq/")
mq_cl = MQClient()

@asynccontextmanager
async def lifespan(_: FastAPI):
    # everything before yield is executed before the app starts up
    # everything after yield is execute after the app shuts down
    await mq_cl.connect(mq_uri)
    await mq_cl.consume("accommodations")
    yield
    await mq_cl.disconnect()


app = FastAPI(lifespan=lifespan)


@app.api_route("/")
async def home():
    txt = "".join(random.choices(string.ascii_letters, k=4))
    await mq_cl.send_message("accommodations", {
        "random_id": txt
    })
    print(f"SENT: {txt}")

    return {
        "hello": "world"
    }
