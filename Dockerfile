# ===== Base Image =====
FROM python:3.10.11-slim-bullseye as base

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

# Use multistage build to install psycopg2 dependencies
# ===== Builder Image =====
FROM base as builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# ===== Final Image =====
FROM base

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libpq-dev

COPY --from=builder /wheels /wheels
COPY --from=builder /code/requirements.txt .
RUN pip install --no-cache /wheels/*

COPY . /code/

EXPOSE 8000

CMD gunicorn rlc_new.wsgi:application --bind 0.0.0.0:8000
