FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# -------------------------------------------------
# 1. Base system + build tools + Python
# -------------------------------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    wget \
    autoconf \
    automake \
    libtool \
    libx11-6 \
    libx11-dev \
    libxaw7-dev \
    libxmu-dev \
    libxpm-dev \
    libreadline-dev \
    libfftw3-dev \
    libncurses5-dev \
    python3 \
    python3-pip \
    python3-venv \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------------------------
# 2. ngspice (already available locally)
# -------------------------------------------------
WORKDIR /opt
COPY ngspice-39 /opt/ngspice-39

RUN cd /opt/ngspice-39 \
    && ./configure --enable-xspice --enable-cider \
    && make -j$(nproc) \
    && make install \
    && ldconfig

# -------------------------------------------------
# 3. Python environment
# -------------------------------------------------
RUN python3 -m venv /opt/pyspice-venv
ENV PATH="/opt/pyspice-venv/bin:$PATH"

RUN pip install --upgrade pip && \
    pip install PySpice numpy matplotlib

# -------------------------------------------------
# 4. Create non-root user
# -------------------------------------------------
RUN useradd -ms /bin/bash eda && \
    mkdir -p /home/eda/projects && \
    chown -R eda:eda /home/eda

USER eda
WORKDIR /home/eda/projects

