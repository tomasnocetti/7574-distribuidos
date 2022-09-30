FROM python:3.9.7-slim

WORKDIR /workspace

COPY ./trending_router/requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
COPY ./trending_router .
COPY ./common ./common

ENTRYPOINT ["/bin/sh"]