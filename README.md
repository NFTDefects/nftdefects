<!-- <h1 align="center">Welcome to NFTDefects 👋</h1> -->
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

  <!-- <a href="https://twitter.com/shall_yangshuo" target="_blank">
    <img alt="Twitter: shall\_yangshuo" src="https://img.shields.io/twitter/follow/shall_yangshuo.svg?style=social" />
  </a> -->
</p>

<br />
<div align="center">
  <!-- <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a> -->

  <h3 align="center">NFTDefects</h3>

  <p align="center">
    1. <a href='./defects_definition/README.md'>Datasets</a> for defining NFT-related contract defects.
    <br/>
    2. Tool NFTGuard for detecting NFT contract defects.
    <br />
    <!-- <a href="https://github.com/othneildrew/Best-README-Template"><strong>Explore the docs »</strong></a> -->
    <!-- <br /> -->
    <!-- <a href="https://github.com/NFTDefects/nftdefects/issues">Report Bug</a>
    ·
    <a href="https://github.com/NFTDefects/nftdefects/issues">Request Feature</a> -->

  </p>
</div>

<!-- > A symbolic execution-based analyzer for detecting NFT-related contract defects. -->

<!-- ### 🏠 [Homepage](https://github.com/NFTDefects/nftdefects) -->

<!-- ### ✨ [Demo](demo url) -->

## Prerequisites

-   python >= 3.6
-   evm >= 1.10.21
    Download version 1.10.21 (tested) from [go-ethereum](https://geth.ethereum.org/downloads) and add executable bins in the `$PATH`.

    ```sh
    wget https://gethstore.blob.core.windows.net/builds/geth-alltools-linux-amd64-1.10.21-67109427.tar.gz
    tar -zxvf geth-alltools-linux-amd64-1.10.21-67109427.tar.gz
    cp geth-alltools-linux-amd64-1.10.21-67109427/evm /usr/local/bin/ #$PATH
    ```

-   solc
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
docker build -t nftdefects:v0.1 .
docker pull ghcr.io/nftdefects/nftdefects:latest
```

## Usage

### Local

For one solidity file.

```sh
python3 tool.py -s test/token.sol -cnames token -j
```

For solidity project (supports newest version crytic-compile toolset). Remember to use remap to link the outside libraries (openzeppelin, etc).

```sh
python3 tool.py -s "path/to/.sol" -rmp "remapping/import_lib/path" -cnames "contract name"
# python3 tool.py -s test/8liens/contracts/8liens/8liensMinter.sol -rmp erc721a=test/8liens/erc721a @openzeppelin=test/8liens/@openzeppelin -cnames \$8liensMinter
```

Other utils.

crawl for contract/dapp's sourcecode by address. see <a href='./crawler/crawl.py'>crawler</a>. The utils can help recover the original structure of the DApp contracts.

### Docker

For the docker image, run with the following command.

```sh
docker run -v test:/NFTGuard/test ghcr.io/nftdefects/nftdefects:latest -s test/token.sol -cnames token -j
```

### Code Structure

-   `inputter`: **_Inputter_** module for compiling the source code of Solidity smart contracts and extracting useful information for further analysis before symbolic execution.
-   `cfg_builder`: **_CFG Builder_** module for analysis, including essential data structures, and symbolic execution of evm opcodes.
-   `feature_detector`: **_Feature Detector_** module of core analysis of finding NFT defects during execution based on 3 operational features (i.e., mapping storage, delete operation, and external invocation) and detection rules.
-   `defect_identifier`: **_Defect Identifier_** module of definition of classes of defect types, and reporter to show the detection results.

### Features

-   Specializing on 5 kinds of defects
    -   _Risky Mutable Proxy_
    -   _ERC-721 Reentrancy_
    -   _Unlimited Minting_
    -   _Public Burn_
    -   _Missing Requirements_
-   NFTGuard is [extensible](https://github.com/enzymefinance/oyente/tree/master) for smart contracts with Solidity versions higher than _0.8.0_.

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
