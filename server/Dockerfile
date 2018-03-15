FROM python:3.5
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
EXPOSE 80
CMD gunicorn --bind 0.0.0.0:80 --worker-class gevent core.wsgi
