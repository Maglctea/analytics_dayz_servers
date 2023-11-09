FROM python:3.11.2-slim

RUN apk add --no-cache tzdata
ENV TZ=Europe/Moscow

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
