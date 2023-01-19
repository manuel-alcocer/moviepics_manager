# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY ../../code/requirements.txt /code
COPY ./entrypoint.sh /code
RUN pip install -r requirements.txt
ENTRYPOINT [ "/bin/sh", "/code/entrypoint.sh" ]
