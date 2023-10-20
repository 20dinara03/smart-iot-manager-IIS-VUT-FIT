import os
from contextlib import asynccontextmanager

from django.core.asgi import get_asgi_application
from starlette.applications import Starlette
from starlette.routing import Mount

from core.broker import broker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")


@asynccontextmanager
async def broker_lifespan(app):
    await broker.start()
    try:
        yield
    finally:
        await broker.close()


application = Starlette(
    routes=(Mount("/", get_asgi_application()),),
    lifespan=broker_lifespan,
)
