FROM python:3.9.7-slim

WORKDIR /workspace

COPY ./watcher/requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
COPY ./watcher .
COPY ./common ./common

ENTRYPOINT ["/bin/sh"]