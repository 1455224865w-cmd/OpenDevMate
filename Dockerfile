FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/1455224865w-cmd/OpenDevMate"
LABEL org.opencontainers.image.licenses="Apache-2.0"

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir . \
    && useradd --create-home --uid 10001 appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /app /data

USER appuser
ENV APP_HOST=0.0.0.0 \
    APP_PORT=8000 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s CMD python -c "import urllib.request; port=open('/tmp/app.port').read().strip(); urllib.request.urlopen('http://127.0.0.1:'+port+'/api/health')"
ENTRYPOINT ["python", "-m", "opendevmate.main"]
