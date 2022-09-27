FROM python:3.9.7-slim

WORKDIR /workspace

COPY ./dropper/requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
COPY ./dropper .
COPY ./common ./common

ENTRYPOINT ["/bin/sh"]