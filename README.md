<p>
  <img alt="Static Badge" src="https://img.shields.io/badge/python-3.6-blue">
  <img alt="Static Badge" src="https://img.shields.io/badge/ubuntu-20.04-yellow">
  <img alt="Static Badge" src="https://img.shields.io/badge/docker-v0.1-purple">
  <a href="doc url" target="_blank">
    <img alt="Documentation" src="https://img.shields.io/badge/documentation-yes-brightgreen.svg" />
  </a>
  <a href="LICSEN" target="_blank">
    <img alt="License: Apache" src="https://img.shields.io/badge/License-Apache-yellow.svg" />
  </a>
  <img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/NFTDefects/nftdefects/publish-docker-image.yml">
  <img alt="GitHub forks" src="https://img.shields.io/github/forks/NFTDefects/nftdefects">
  <img alt="GitHub forks" src="https://img.shields.io/github/stars/NFTDefects/nftdefects">
</p>

<br />
<div align="center">

  <h3 align="center">NFTDefects</h3>

  <p align="center">
    1. <a href='./defects_definition/README.md'>Datasets</a> for defining NFT-related contract defects.
    <br/>
    2. Tool NFTGuard for detecting NFT contract defects.
    <br />
  </p>
</div>

## Prerequisites

-   Python >= 3.6.
-   evm >= 1.10.21.
    Download version 1.10.21 (tested) from [go-ethereum](https://geth.ethereum.org/downloads) and add executable bins in the `$PATH`.

    ```sh
    wget https://gethstore.blob.core.windows.net/builds/geth-alltools-linux-amd64-1.10.21-67109427.tar.gz
    tar -zxvf geth-alltools-linux-amd64-1.10.21-67109427.tar.gz
    cp geth-alltools-linux-amd64-1.10.21-67109427/evm /usr/local/bin/ #$PATH
    ```

-   solc.
    Recommend solc-select to manage Solidity compiler versions.

    ```sh
    pip3 install solc-select
    ```

## Install

1. Python dependencies installation.

```sh
pip3 install -r requirements.txt
```

2. Or you can build or pull the docker image.

```sh
docker build -t nftdefects:local . # local build
docker pull ghcr.io/nftdefects/nftdefects:latest # remote pull
```

## Usage

### Local

For one solidity file.

```sh
python3 tool.py -s test/token.sol -cnames token -j -glt 200 -ll 50 -dl 500
```

To test a specifc function, use `-fselector` to specifiy the function selector (`-as` option is provided for automatical solc version switch).

```sh
python3 tool.py -s test/toadz.sol -cnames CreatureToadz -fselector 40c10f19 -as
```

For solidity project (supports newest version crytic-compile toolset). Remember to use remap to link the outside libraries (openzeppelin, etc).

```sh
python3 tool.py -s "path/to/.sol" -rmp "remapping/import_lib/path" -cnames "contract name"
# example
python3 tool.py -s test/8liens/contracts/8liens/8liensMinter.sol -rmp erc721a=test/8liens/erc721a @openzeppelin=test/8liens/@openzeppelin -cnames \$8liensMinter
```

Other utils: contract/project source code crawler (with complete code structure) from EtherScan. See <a href='./crawler/crawl.py'>crawler.py</a>. The utils can help recover the original structure of the DApp contracts to be fed into NFTGuard with remap configuration.

```sh
python3 crawl.py --dir ./0x --caddress 0x # 0x is the contract address
```

### Docker

For the docker image, run with the following command.

```sh
docker run -v test:/NFTGuard/test ghcr.io/nftdefects/nftdefects:latest -s test/token.sol -cnames token -j
```

## Publication

This repository was proposed in the [ISSTA'23 paper](<(https://dl.acm.org/doi/10.1145/3597926.3598063).>), and we would really appreciate for your citation if this repo helps you.

```latex
@inproceedings{yang2023definition,
  title={Definition and Detection of Defects in NFT Smart Contracts},
  author={Yang, Shuo and Chen, Jiachi and Zheng, Zibin},
  booktitle={Proceedings of the 32nd ACM SIGSOFT International Symposium on Software Testing and Analysis},
  pages={373--384},
  year={2023}
}
```

## 📝 License

Copyright © 2024 [Shuo Yang](https://github.com/shuo-young).<br />
This project is [Apache](https://github.com/NFTDefects/nftdefects/blob/master/LICENSE) licensed.
