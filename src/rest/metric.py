from typing import TypedDict

from django.http import Http404
from rest_framework import serializers, views
from rest_framework.response import Response

from grafita.models import Device, Metric


class MetricSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Metric
        fields = ["time", "value", "device", "attribute"]


Dataframe: TypedDict = TypedDict("Response", {"time": str, "value": float})


class MetricView(views.APIView):
    def get(self, request, device_pk, _=None):
        df = self.get_metrics_dataframe(self.get_device(device_pk))
        return Response(df)

    @staticmethod
    def get_metrics_dataframe(device: Device) -> dict[str, dict[str, list[Dataframe]]]:
        df: dict[str, dict[str, list[Dataframe]]] = {}  # type: ignore
        metrics = Metric.objects.filter(device=device).values("time", "value", "attribute").order_by("attribute")
        for metric in metrics.iterator():
            attr = df.get(metric["attribute"])
            if attr:
                attr["time"].append(metric["time"])
                attr["value"].append(metric["value"])
            else:
                df[metric["attribute"]] = {"time": [metric["time"]], "value": [metric["value"]]}

        return df

    @staticmethod
    def get_device(device_pk: int) -> Device:
        try:
            return Device.objects.filter(id=device_pk).get()
        except Device.DoesNotExist:
            raise Http404
