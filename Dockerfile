FROM python:3.11.14-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN useradd \
    --create-home \
    --uid 1000 \
    --shell /usr/sbin/nologin \
    appuser

COPY requirements.txt .

RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

COPY --chown=appuser:appuser backend ./backend
COPY --chown=appuser:appuser frontend ./frontend
COPY --chown=appuser:appuser ml ./ml
COPY --chown=appuser:appuser models ./models

USER appuser

EXPOSE 7860

HEALTHCHECK \
    --interval=30s \
    --timeout=5s \
    --start-period=15s \
    --retries=3 \
    CMD ["python", "-c", "import os, urllib.request; port = os.environ.get('PORT', '7860'); urllib.request.urlopen(f'http://127.0.0.1:{port}/api/health', timeout=3)"]

CMD ["sh", "-c", "python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-7860}"]