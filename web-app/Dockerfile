# syntax=docker/dockerfile:1

FROM python:3.10-alpine

WORKDIR /web-app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

ENV FLASK_MACHINEID=tx123

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0" ]