FROM python:3.11-alpine3.18

# install dependencies
WORKDIR /www
RUN addgroup -S grafita && adduser -S grafita -G grafita

# install poetry and dependencies
RUN apk add libpq-dev gcc python3-dev musl-dev libffi-dev
RUN pip install poetry

USER grafita

COPY --chown=grafita:grafita poetry.lock pyproject.toml /www/
RUN poetry install --no-interaction --only main

# copy entrypoint.sh
COPY --chown=grafita:grafita docker/entrypoint.sh .
RUN chmod +x entrypoint.sh

# copy project
COPY --chown=grafita:grafita src ./src


# run entrypoint.sh
ENTRYPOINT ["/www/entrypoint.sh"]
