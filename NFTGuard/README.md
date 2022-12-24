# NFTGuard

## Description

A static analysis tool for detecting NFT-related contract defects based on a symbolic execution framework.

## Features

- Specializing on 5 kind of defects
  - Risky Mutable Proxy
  - ERC-721 Reentrancy
  - Unlimited Minting
  - Public Burn
  - Standard Violation
- NFTGuard is also extensible for smart contracts with Solidity versions higher than 0.8.0.
- NFTGuard found 1,331 NFT smart contracts containing at least one of the 5 defects in 16,527 contracts from Etherscan.
  The related dataset can be found at [NFTDefects](https://github.com/NFTDefects/nftdefects).

## Code Structure

- `input`: module for compiling the source code of Solidity smart contracts and extracting useful information for further analysis before symbolic execution.
- `evm`: data structures for symbolic execution.
- `defects`: definition of classes of defect types.
- `analysis`: core analysis of finding defects during execution.
- `contracts`: test demo for running NFTGurad.
- `global_params.py`: global params for analysis.
- `sym_exec.py`: symbolic execution of evm opcodes.
- `utils.py`: functions for utilities.
- `tool.py`: interfaces for input and output.

## Usage

1. Prepare requirements.

- Python environment: please use Python 3.8, which is recommended (tested).
- Python dependencies: please use pip to install dependencies in `requirements.txt`.

```shell
  $ pip3 install -r requirements.txt
```

- `solc`: please use solc-select which is downloaded in dependencies to install Solidity 0.8.16 (recommended) and switch to it.

```shell
  $ solc-select install 0.8.16
  $ solc-select use 0.8.16
```

- `evm`: please download version 1.10.21 (tested) from [go-ethereum](https://geth.ethereum.org/downloads) and add executable bins in the `$PATH`. Ubuntu users can use PPA:

```shell
 $ sudo apt-get install software-properties-common
 $ sudo add-apt-repository -y ppa:ethereum/ethereum
 $ sudo apt-get update
 $ sudo apt-get install ethereum
```

2. Demo test:

```shell
$ python3 tool.py -s contracts/demo.sol -cnames token
```

The result would show in 2~3 minutes in the console. 3. Demo output:

```shell
INFO:root:contract contracts/demo.sol:token:
INFO:sym_exec:  ============ Results of contracts/demo.sol:token===========
INFO:root:Building CFG...
INFO:root:instruction size: 5960
INFO:sym_exec:    EVM Code Coverage:                     97.1%
INFO:sym_exec:    Standard Violation Defect:             False
INFO:sym_exec:    ERC721-Reentrancy Defect:              True
INFO:sym_exec:    Risky Proxy Defect:                    True
INFO:sym_exec:    Unlimited Minting Defect:              True
INFO:sym_exec:    Public Burn Defect:                    True
INFO:sym_exec:contracts/demo.sol:22:13: Warning: ERC721 Reentrancy Defect.
           _safeMint(msg.sender, totalSupply() + i)
INFO:sym_exec:contracts/demo.sol:49:10: Warning: Risky Mutable Proxy Defect.
        proxyRegistryAddress = _proxyRegistryAddress
INFO:sym_exec:contracts/demo.sol:37:13: Warning: Unlimited Minting Defect.
           _safeMint(_to, supply+i)
INFO:sym_exec:contracts/demo.sol:44:10: Warning: Public Burn Defect.
        _burn(tokenId)
INFO:sym_exec:  ====== Analysis Completed ======
```
