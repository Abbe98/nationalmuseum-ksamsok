FROM python:3.7.5-slim-buster

COPY requirements.txt .env ./
COPY ./nationalmuseum-ksamsok ./nationalmuseum-ksamsok

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn

WORKDIR /nationalmuseum-ksamsok

EXPOSE 5000

CMD ["gunicorn"  , "-b", "0.0.0.0:5000", "app:app"]
