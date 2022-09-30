FROM python:3.9.7-slim

WORKDIR /workspace

COPY ./trending_instance/requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
COPY ./trending_instance .
COPY ./common ./common

ENTRYPOINT ["/bin/sh"]