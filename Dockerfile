ARG ETHEREUM_VERSION=alltools-v1.10.21
ARG SOLC_VERSION=0.8.16

FROM ethereum/client-go:${ETHEREUM_VERSION} AS geth
FROM ethereum/solc:${SOLC_VERSION} AS solc

FROM python:3.10-slim AS cli

LABEL maintainer="Shuo Yang <https://github.com/shuo-young>"

ENV PYTHONIOENCODING=utf-8

# Install build dependencies and runtime tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Install geth evm and solc from official images
COPY --from=geth /usr/local/bin/evm /usr/local/bin/evm
COPY --from=solc /usr/bin/solc /usr/bin/solc

WORKDIR /NFTGuard

# Leverage Docker layer caching for deps
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copy source
COPY . .

ENTRYPOINT ["python3", "/NFTGuard/tool.py"]
