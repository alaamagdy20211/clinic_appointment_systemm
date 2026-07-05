FROM python:3.13-slim-bookworm

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code
RUN apt-get update && apt-get install -y netcat-openbsd

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .
# COPY entrypoint.sh /entrypoint.sh
# RUN chmod +x /entrypoint.sh

# CMD ["/entrypoint.sh"]