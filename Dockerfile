FROM python:3.12-alpine3.17
WORKDIR /usr/src/app

RUN apk add --no-cache \
    gcc \
    musl-dev \
    mariadb-dev \
    mysql-dev \
    python3-dev \
    pkgconfig

COPY requirements.txt  requirements.txt

RUN pip install -r requirements.txt

COPY . . 

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]