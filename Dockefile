FROM ubuntu:12.04
MAINTAINER menglike

RUN apt-get update
RUN apt-get install -y python-software-properties python-pip3

COPY * /opt

RUN pip3 install -r /opt/requirement.txt
WORKDIR /opt
RUN python manage.py runserver 0.0.0.0:5001
