# NFTGuard

## Description

A static analysis tool for detecting NFT-related contract defects based on a symbolic execution framework.

## Features

- Specializing on 5 kinds of defects
  - *Risky Mutable Proxy*
  - *ERC-721 Reentrancy*
  - *Unlimited Minting*
  - *Public Burn*
  - *Missing Requirements*
- NFTGuard is also extensible for smart contracts with Solidity versions higher than *0.8.0*.
- NFTGuard found 1,331 NFT smart contracts containing at least one of the 5 defects in 16,527 contracts from Etherscan.
  The related dataset can be found at [NFTDefects](https://github.com/NFTDefects/nftdefects).

## Code Structure

The design refers to the architecture shown below:

<img src="./images/arch.png" alt="arch" style="zoom: 50%;" />

- `inputter`: **_Inputter_** module for compiling the source code of Solidity smart contracts and extracting useful information for further analysis before symbolic execution.
- `cfg_builder`: **_CFG Builder_** module for analysis, including essential data structures, and symbolic execution of evm opcodes.
- `feature_detector`: **_Feature Detector_** module of core analysis of finding NFT defects during execution based on 3 operational features (i.e., mapping storage, delete operation, and external invocation) and detection rules.
- `defect_identifier`: **_Defect Identifier_** module of definition of classes of defect types, and reporter to show the detection results.
- `test`: test demo for running NFTGurad.
- `global_params.py`: global params for analysis.
- `tool.py`: interfaces for input and output.
- `requirements.txt`: required packages for running tool.

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

- `evm`: please download version 1.10.21 (tested) from [go-ethereum](https://geth.ethereum.org/downloads) and add executable bins in the `$PATH`. Ubuntu users can also use PPA:

  ```shell
  $ sudo apt-get install software-properties-common
  $ sudo add-apt-repository -y ppa:ethereum/ethereum
  $ sudo apt-get update
  $ sudo apt-get install ethereum
  ```

1. Demo test:

   ```shell
   $ python3 tool.py -s test/demo.sol -cnames token -j
   ```

   It would take minutes to show the result in the console, and there will be a json file to store the results in the same directory of the tested contract. Below image shows the output in the console.
   
   *Processing*
   ![output](./images/processing.png)
   *Result*
   ![output](./images/output.png)
