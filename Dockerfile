FROM ubuntu:latest
LABEL authors="yottso"

FROM python:3.10

RUN mkdir /code

WORKDIR /code

COPY requirements.txt /code/requirements.txt

#
RUN pip install  --upgrade -r /code/requirements.txt

#
COPY . /code

WORKDIR /code/app
#
CMD gunicorn app.main:app --bind=0.0.0.0:8000