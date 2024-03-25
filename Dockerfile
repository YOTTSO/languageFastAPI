FROM ubuntu:latest
LABEL authors="yottso"

FROM python:3.10

RUN mkdir /code

WORKDIR /code

COPY requirements.txt /code/requirements.txt

#
RUN pip install  --upgrade -r /code/requirements.txt

#
COPY . /code/

#
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]