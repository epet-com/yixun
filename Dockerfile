FROM ubuntu:16.04
MAINTAINER menglike
RUN apt-get update
#安装python3.5
RUN apt-get install -y python3.5
#添加项目代码
ADD project.tar.gz /opt/
#工作目录
WORKDIR /opt
#安装pip3
RUN python3.5 pip.py
#安装项目需要的扩展
RUN pip3 install -r requirements.txt
#启动web
CMD ["python3.5","manage.py","runserver","0.0.0.0:5003"]
