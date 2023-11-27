import logging

from typing import Final

from asgiref.sync import sync_to_async
from django.contrib.auth import authenticate
from django.utils import timezone
from faststream.nats.annotations import NatsMessage

from core.broker import broker
from grafita.models import Metric

DeviceIDHeader: Final[str] = "X-Device-ID"


async def auth_broker(username: str, password: str) -> bool:
    user = await sync_to_async(authenticate)(username=username, password=password)
    # check if user has group broker
    if not user:
        return False

    broker_group = await sync_to_async(user.groups.filter)(name="broker")
    return await sync_to_async(broker_group.exists)()


@broker.subscriber("metric")
async def register_metric(msg: NatsMessage) -> None:
    headers = msg.headers

    if not await auth_broker(headers.get("username"), headers.get("password")):
        logging.warning(f"Not authorized message from {headers.get('username')}")
        return

    device_id = headers.get(DeviceIDHeader)
    if not device_id:
        logging.warning(f"bad formatted message. No {DeviceIDHeader} header")
        return

    attr_dict = msg.decoded_body
    if not attr_dict:
        logging.warning(f"bad formatted message. No body")
        return

    time = attr_dict.pop("time", None) or timezone.now()
    for attr, value in attr_dict.items():
        await sync_to_async(Metric.objects.create)(
            device_id=device_id, time=time, attribute=attr, value=value
        )
