FROM python:3.7-slim-buster

RUN mkdir -pv /home/project/flask_app
RUN mkdir -pv /var/ttn_tracker/ssl_certs

WORKDIR /home/project/flask_app

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y build-essential

COPY requirements.txt /home/project/flask_app
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . /home/project/flask_app

RUN /bin/bash /home/project/flask_app/ssl-certs-generate.sh
