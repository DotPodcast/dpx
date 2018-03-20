FROM python:3.6

RUN python -m ensurepip && pip install --upgrade pip setuptools rq

ADD . /code/
WORKDIR /code
RUN pip install -r requirements.txt
CMD pytest tests.py
