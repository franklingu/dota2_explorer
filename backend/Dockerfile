# Dockerfile for deployment
FROM ubuntu:16.04

MAINTAINER franklingu

# Replace shell with bash so we can source files
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y build-essential \
    libpq-dev libssl-dev libffi-dev python3-pip && \
    apt-get clean
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY ./backend/requirements.txt /usr/src/app/
RUN pip3 install -U pip setuptools
RUN pip3 install -r requirements.txt
RUN pip3 install uwsgi
RUN mkdir -p /var/run/uwsgi \
    /var/log/uwsgi \
    /var/log/app \
    /usr/src/app/run \
    /var/data/app
COPY . /usr/src/app/
