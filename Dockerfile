FROM ubuntu:latest
LABEL authors="yottso"

FROM python:3.10

RUN mkdir /code

WORKDIR /code

COPY requirements.txt /code/requirements.txt

#
RUN pip install -r /code/requirements.txt
RUN pip install https://github.com/explosion/spacy-models/releases/download/ru_core_news_sm-3.7.0/ru_core_news_sm-3.7.0.tar.gz

#
COPY . /code/

#
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]