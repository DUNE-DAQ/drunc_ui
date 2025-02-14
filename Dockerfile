FROM python:3.10-slim-bookworm AS python

FROM python AS build

RUN pip install --root-user-action ignore pipx==1.6
RUN pipx install poetry==1.8
COPY pyproject.toml poetry.lock /
RUN /root/.local/bin/poetry config virtualenvs.create false && \
    /root/.local/bin/poetry install --no-root --no-directory --only main --only postgres

FROM python

COPY --from=build /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=build /usr/local/bin /usr/local/bin
EXPOSE 8000
COPY --chown=nobody:nogroup . /usr/src/app
RUN apt-get update && apt-get install -y git

RUN cd / && \
    git clone https://github.com/DUNE-DAQ/drunc.git && \
    cd drunc && \
    pip install -e .
RUN cd / && \
    git clone https://github.com/DUNE-DAQ/druncschema.git && \
    cd druncschema && \
    pip install -e .


WORKDIR /usr/src/app
USER nobody
