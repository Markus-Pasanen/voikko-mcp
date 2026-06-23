FROM python:3.11-slim

LABEL org.opencontainers.image.source=https://github.com/Markus-Pasanen/voikko-mcp
LABEL org.opencontainers.image.description="Finnish language verification MCP server powered by libvoikko"
LABEL org.opencontainers.image.licenses=GPL-3.0-or-later

RUN apt-get update && apt-get install -y --no-install-recommends \
    libvoikko-dev \
    voikko-fi \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

EXPOSE 8000

CMD ["python", "server.py"]
