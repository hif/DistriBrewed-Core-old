FROM python:3-alpine

RUN apk add --no-cache g++ musl-dev

ENV DIR /distribrewed
ADD . ${DIR}
WORKDIR ${DIR}

RUN pip install -r requirements.txt
RUN pip install .