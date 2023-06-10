FROM python:3.10.8

WORKDIR app

COPY requirements.txt requirements.txt
RUN apt -y update \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .