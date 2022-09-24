FROM python:3.9.7-slim

WORKDIR /workspace

COPY ./joiner/requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
COPY ./joiner /
COPY ./common /workspace/common

ENTRYPOINT ["/bin/sh"]