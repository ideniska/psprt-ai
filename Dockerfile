FROM python:3.10

ENV HOME=/app
ENV PYTHONUNBUFFERED 1

WORKDIR $HOME

RUN pip install --upgrade pip poetry

COPY ["pyproject.toml", "poetry.lock", "$HOME/"]

RUN POETRY_VIRTUALENVS_CREATE=false poetry install --no-interaction --no-ansi

COPY . $HOME
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
