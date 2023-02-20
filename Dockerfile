FROM python:3.10.9

ENV HOME=/app
ENV PYTHONUNBUFFERED 1

WORKDIR $HOME

RUN apt-get update && apt-get -y install cmake protobuf-compiler
RUN pip install --upgrade pip poetry

COPY ["pyproject.toml", "poetry.lock", "$HOME/"]

RUN POETRY_VIRTUALENVS_CREATE=false poetry install --no-interaction --no-ansi --with prod

COPY . $HOME
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

EXPOSE 9000
ENTRYPOINT ["/entrypoint.sh"]
