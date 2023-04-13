# pull official base image
FROM node:13.12.0-alpine

# set working directory
WORKDIR /ui

# add `/app/node_modules/.bin` to $PATH
ENV PATH /ui/node_modules/.bin:$PATH

# install app dependencies
COPY package.json ./
COPY package-lock.json ./
RUN apk add --no-cache git
RUN apk add --no-cache bash
RUN npm install --silent
RUN npm install react-scripts@3.4.1 -g --silent

# add app
COPY . ./

RUN chmod +x wait-for-it.sh