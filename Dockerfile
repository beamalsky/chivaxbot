FROM python:3.7

LABEL maintainer "Bea Malsky <beamalsky@gmail.com>"

RUN mkdir /app
WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
