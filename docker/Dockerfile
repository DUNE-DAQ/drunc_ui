FROM debian:bookworm-slim

ARG NIGHTLY=NFD_DEV_260216_A9

RUN apt-get update && \
    apt-get install -y --no-install-recommends libssl3 && \
    rm -rf /var/lib/apt/lists/*

ENV PATH=/root/app/${NIGHTLY}/.venv/bin:${PATH}

COPY ${NIGHTLY} /root/app/${NIGHTLY}

COPY manage.py /root/app/
COPY staticfiles /root/app/staticfiles
COPY drunc_ui /root/app/drunc_ui
COPY ers /root/app/ers
COPY interfaces /root/app/interfaces
COPY main /root/app/main
COPY controller /root/app/controller
COPY process_manager /root/app/process_manager
COPY session_manager /root/app/session_manager

WORKDIR /root/app
RUN echo "cd /root/app/${NIGHTLY}" >> entrypoint.sh && \
    echo ". env.sh" >> entrypoint.sh && \
    echo "cd /root/app" >> entrypoint.sh && \
    echo "gunicorn drunc_ui.wsgi:application --bind 0.0.0.0:8000" >> entrypoint.sh && \
    chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/usr/bin/bash", "-c", "/root/app/entrypoint.sh"]
