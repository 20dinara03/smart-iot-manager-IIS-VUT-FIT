from django.apps import AppConfig


class MQConfig(AppConfig):
    name = "mq"

    def ready(self):
        from mq.input import register_metric # noqa
