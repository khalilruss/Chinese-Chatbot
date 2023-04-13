FROM python:3.7 as builder

RUN pip install fasttext gensim

COPY preprocess_vec_model.py .

RUN python preprocess_vec_model.py &&\
    rm cc.zh.300.bin.gz cc.zh.300.bin cc.zh.100.bin

FROM nvidia/cuda:11.2.0-base-ubuntu18.04

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

RUN mkdir /chatbot

COPY requirements.txt /chatbot

WORKDIR /chatbot

RUN pip --no-cache-dir install -r requirements.txt

RUN mkdir /word_vectors

COPY --from=builder cc.zh.100.vec cc.zh.100.vec.vectors_ngrams.npy cc.zh.100.vec.vectors_vocab.npy /word_vectors/

COPY . /chatbot

EXPOSE 8000

WORKDIR /chatbot/app