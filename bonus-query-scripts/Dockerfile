# syntax=docker/dockerfile:1

FROM python:3.10-alpine

ADD query_maker.py .
RUN pip install requests

ENTRYPOINT [ "python3", "./query_maker.py"]