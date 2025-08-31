ARG ETHEREUM_VERSION=alltools-v1.10.21
ARG SOLC_VERSION=0.8.16

FROM ethereum/client-go:${ETHEREUM_VERSION} as geth
FROM ethereum/solc:${SOLC_VERSION} as solc

FROM ubuntu:20.04 as CLI

ARG NODEREPO=node_8.x

LABEL maintainer "Shuo Yang <https://github.com/shuo-young>"

SHELL ["/bin/bash", "-c", "-l"]
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget unzip python-virtualenv git build-essential software-properties-common curl
RUN curl -s 'https://deb.nodesource.com/gpgkey/nodesource.gpg.key' | apt-key add -
RUN apt-add-repository "deb https://deb.nodesource.com/${NODEREPO} $(lsb_release -c -s) main"
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN apt-get update
RUN apt-get install -y musl-dev golang-go python3 python3-pip python-pip \
        bison zlib1g-dev libyaml-dev libssl-dev libgdbm-dev libreadline-dev \
	zlib1g-dev libreadline-dev libyaml-dev libsqlite3-dev sqlite3 \
        libxml2-dev libxslt1-dev libcurl4-openssl-dev libffi-dev nodejs yarn && \
        apt-get clean

# Instsall geth from official geth image
COPY --from=geth /usr/local/bin/evm /usr/local/bin/evm

# Install solc from official solc image
COPY --from=solc /usr/bin/solc /usr/bin/solc

ENV PYTHONIOENCODING=utf-8 

COPY . /NFTGuard
RUN cd /NFTGuard && pip3 install -r requirements.txt

WORKDIR /NFTGuard
ENTRYPOINT ["python3", "/NFTGuard/tool.py"]