# Build context is the repository root (see docker-compose.yml).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /srv

COPY app/requirements.txt app/requirements.txt
RUN pip install -r app/requirements.txt

COPY app/ app/
RUN chmod +x app/entrypoint.sh \
    && useradd --create-home --uid 1000 stand
USER stand

EXPOSE 8000
ENTRYPOINT ["app/entrypoint.sh"]
