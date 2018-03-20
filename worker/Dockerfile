FROM python:3.6

RUN apt-get update
RUN apt-get install -y \
  cmake \
  curl \
  g++ \
  gcc \
  libxml2 \
  libxml2-dev

RUN python -m ensurepip && pip install --upgrade pip setuptools rq

ADD . /code/
WORKDIR /code
RUN pip install -r requirements.txt
CMD ["sh", "-c", "rq worker -u ${REDIS_URL}"]
