import os

from faststream.nats import NatsBroker

broker = NatsBroker(
    servers=[f"nats://{os.environ['NATS_SERVER']}:4222"],
)