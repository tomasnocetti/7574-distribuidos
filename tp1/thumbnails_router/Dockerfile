FROM python:3.9.7-slim

WORKDIR /workspace

COPY ./thumbnails_router/requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
COPY ./thumbnails_router .
COPY ./common ./common

ENTRYPOINT ["/bin/sh"]