import logging
from typing import Final

from asgiref.sync import sync_to_async
from django.utils import timezone
from faststream.nats.annotations import NatsMessage

from core.broker import broker
from grafita.models import Metric

DeviceIDHeader: Final[str] = "X-Device-ID"


@broker.subscriber("metric")
async def register_metric(msg: NatsMessage) -> None:
    headers = msg.headers
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
