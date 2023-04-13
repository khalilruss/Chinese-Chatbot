FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

RUN mkdir /grammar_extractor

COPY requirements.txt /grammar_extractor

WORKDIR /grammar_extractor

RUN pip --no-cache-dir install -r requirements.txt

COPY . /grammar_extractor

EXPOSE 8002

WORKDIR /grammar_extractor/app