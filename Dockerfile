FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    git \
    wget \
    ngspice \
    swig \
    python3-dev \
    pkg-config \
    graphviz \
    libngspice0-dev \
    ; \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app


# Install PyTorch CPU-only first
RUN pip install --no-cache-dir torch==2.1.2 --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]
