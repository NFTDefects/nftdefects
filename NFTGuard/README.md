# NFTGuard

## Description

A static analysis tool for detecting NFT-realted contract defects based on a symbolic execution framework.

## Strengths

- The first symbolic execution tool focusing on NFT-related contract defects
- Specializing on 5 kind of defects
    - Risky Mutable Proxy
    - ERC-721 Reentrancy
    - Unlimited Minting
    - Public Burn
    - Standard Violation
- NFTGuard is also exetensible for smart contracts with a higher version of Solidity 0.8.0+
- NFTGuard found 1,331 NFT smart contracts containing at least one of the 5 defects in 16,527 contracts from Etherscan.
  The related dataset can be found at [NFTDefects](https://github.com/NFTDefects/nftdefects).

## Usage

1. Prepare requirements.
  


- Conda ENV: Enter the directory of NFTGuard and create a virtual environment via conda and exported yaml `environment.yaml` to start.

   ```shell
   conda env create -f environment.yaml
   ```

- Pip ENV: Enter the directory and use pip to install dependencies via `requirements.txt`, the python version `3.8.x` is tested (recommended).

   ```shell
   pip install -r requirements.txt
   ```
- The solidity compiler `solc` is required (0.8.16 recommended). You can also down `solc-select`:
  
    ```shell
    pip install solc-select
    solc-select install 0.8.16
    solc-select use 0.8.16
    ```

2. Demo input:

```shell
python3 tool.py -s contracts/reentrancy/demo.sol -cnames token
```

3. Demo output:

```shell
INFO:root:contract contracts/reentrancy/demo.sol:token:
INFO:symExec:   ============ Results of contracts/reentrancy/demo.sol:token===========
INFO:root:Building CFG...
INFO:root:instruction size: 5684
INFO:symExec:     EVM Code Coverage:                     87.8%
INFO:symExec:     Standard Violation Defect:             False
INFO:symExec:     ERC721-Reentrancy Defect:              True
INFO:symExec:     Risky Proxy Defect:                    False
INFO:symExec:     Unlimited Minting Defect:              False
INFO:symExec:     Public Burn Defect:                    False
INFO:symExec:contracts/reentrancy/demo.sol:65:13: Warning: ERC721 Reentrancy Defect.
            _safeMint(msg.sender, totalSupply() + i)
INFO:symExec:   ====== Analysis Completed ======
```
