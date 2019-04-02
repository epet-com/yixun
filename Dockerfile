FROM python:3.5
MAINTAINER menglike
COPY * /opt/
RUN pip install -r /opt/requirements.txt
WORKDIR /opt
CMD ["python","manage.py","runserver","0.0.0.0:5003"]
