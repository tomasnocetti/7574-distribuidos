FROM python:3.9.7-slim

WORKDIR /workspace

COPY ./client/requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
COPY ./client .
COPY ./common ./common


ENTRYPOINT ["/bin/sh"]