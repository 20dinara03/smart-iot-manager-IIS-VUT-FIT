from abc import ABCMeta, abstractmethod
from typing import TypeVar, TYPE_CHECKING

from django.db.models import QuerySet

if TYPE_CHECKING:
    from grafita.models import Metric

kpi_registry: dict[str, type["AnyKpi"]] = {}


def kpi_list() -> list[str]:
    return list(kpi_registry.keys())


class KPIMeta(ABCMeta):
    def __new__(cls, name: str, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        if name not in ("AbstractKPI", "_AbstractKPI"):
            kpi_registry[name.lower()] = new_class  # type: ignore
        return new_class


class _AbstractKPI(metaclass=KPIMeta):
    __slots__ = ()


T = TypeVar("T")
Numeric = int | float


class AbstractKPI(_AbstractKPI):
    @staticmethod
    @abstractmethod
    def validate(value: T, query_set: QuerySet["Metric"]) -> bool:
        raise NotImplementedError


AnyKpi: TypeVar = TypeVar("AnyKpi", bound=AbstractKPI)


class Higher(AbstractKPI):
    @staticmethod
    def validate(value: Numeric, query_set: QuerySet["Metric"]) -> bool:
        return query_set.filter(value__gt=value).count() == 0


class Lower(AbstractKPI):
    @staticmethod
    def validate(value: Numeric, query_set: QuerySet["Metric"]) -> bool:
        return query_set.filter(value__lt=value).count() == 0


class Between(AbstractKPI):
    @staticmethod
    def validate(value: tuple[Numeric, Numeric], query_set: QuerySet["Metric"]) -> bool:
        return query_set.filter(value__range=value).count() == 0
