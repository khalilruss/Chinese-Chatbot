FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

RUN mkdir /classifier

COPY requirements.txt /classifier

WORKDIR /classifier

RUN pip --no-cache-dir install -r requirements.txt

COPY . /classifier

EXPOSE 8001

WORKDIR /classifier/app

