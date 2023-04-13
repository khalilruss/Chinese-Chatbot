FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

RUN mkdir /user_auth

COPY requirements.txt /user_auth

WORKDIR /user_auth

RUN pip --no-cache-dir install -r requirements.txt

COPY . /user_auth

EXPOSE 8005

WORKDIR /user_auth/app
