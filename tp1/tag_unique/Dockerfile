FROM python:3.9.7-slim

WORKDIR /workspace

COPY ./tag_unique/requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
COPY ./tag_unique .
COPY ./common ./common

ENTRYPOINT ["/bin/sh"]