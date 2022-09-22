FROM python:3.9.7-slim

COPY client/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY client /

ENTRYPOINT ["/bin/sh"]