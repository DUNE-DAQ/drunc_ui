#!/usr/bin/bash

NIGHTLY=NFD_DEV_260216_A9

docker run --rm \
  -e HOST_USER=$(id -u) \
  -e HOST_GROUP=$(id -g) \
  -e NIGHTLY=${NIGHTLY} \
  -v ${PWD}:/root/app \
  -v /cvmfs:/cvmfs:shared \
  python:3.10-slim-bookworm \
  bash -lc '
    cd /root/app

    . /cvmfs/dunedaq.opensciencegrid.org/setup_dunedaq.sh
    setup_dbt latest_v5
    dbt-create -n ${NIGHTLY}
    cd /root/app/${NIGHTLY}
    . env.sh
    dbt-build

    pip install -U pip
    pip install \
      django \
      whitenoise \
      crispy-bootstrap5 \
      django-tables2 \
      django-bootstrap5 \
      django-stubs-ext \
      django-crispy-forms \
      pytest-asyncio \
      requests \
      psycopg[binary] \
      gunicorn

    cd /root/app
    python manage.py collectstatic --noinput

    chown -R ${HOST_USER}:${HOST_GROUP} ${NIGHTLY}
    chown -R ${HOST_USER}:${HOST_GROUP} staticfiles
  '
