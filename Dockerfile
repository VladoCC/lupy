FROM python:3-slim

RUN apt-get update && apt-get -y install gcc && apt-get clean

WORKDIR /install
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

WORKDIR /compiler
