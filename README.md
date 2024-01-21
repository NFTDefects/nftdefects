# NFTDefects

![Static Badge](https://img.shields.io/badge/licence-apache-red)

## NFTGuard

An analyzer for detecting NFT-related contract defects based on a symbolic execution framework.

### Quick Start

1. Prepare requirements.

-   Python environment: please use Python 3.8, which is recommended (tested).
-   Python dependencies: please use pip to install dependencies in `requirements.txt`.

    ```shell
      $ pip3 install -r requirements.txt
    ```

-   `solc`: please use solc-select to install Solidity 0.8.16 (recommended) and switch to it.

    ```shell
      $ pip3 install solc-select==0.2.1
      $ solc-select install 0.8.16
      $ solc-select use 0.8.16
    ```

-   `evm`: please download version 1.10.21 (tested) from [go-ethereum](https://geth.ethereum.org/downloads) and add executable bins in the `$PATH`.

2. Demo test:

    ```shell
    $ python3 tool.py -s test/demo.sol -cnames token -j
    ```

    It would take minutes to show the result in the console, and there will be a json file to store the results in the same directory of the tested contract. Below image shows the output in the console.

    _Processing_
    ![output](./images/processing.png)
    _Result_
    ![output](./images/output.png)

3. Docker run:
   You can also build docker and run with it.
    ```shell
    $ docker build -t nftdefects:v0.1 .
    ```
    Then run docker image.
    ```shell
    $ docker run -v test:/NFTGuard/test nftdefects:v0.1 -s test/demo.sol -cnames token -j
    ```

### Code Structure

The design refers to the architecture shown below:

<img src="./images/arch.png" alt="arch" style="zoom: 50%;" />

-   `inputter`: **_Inputter_** module for compiling the source code of Solidity smart contracts and extracting useful information for further analysis before symbolic execution.
-   `cfg_builder`: **_CFG Builder_** module for analysis, including essential data structures, and symbolic execution of evm opcodes.
-   `feature_detector`: **_Feature Detector_** module of core analysis of finding NFT defects during execution based on 3 operational features (i.e., mapping storage, delete operation, and external invocation) and detection rules.
-   `defect_identifier`: **_Defect Identifier_** module of definition of classes of defect types, and reporter to show the detection results.
-   `test`: test demo for running NFTGurad.
-   `global_params.py`: global params for analysis.
-   `tool.py`: interfaces for input and output.
-   `requirements.txt`: required packages for running tool.

### Features

-   Specializing on 5 kinds of defects
    -   _Risky Mutable Proxy_
    -   _ERC-721 Reentrancy_
    -   _Unlimited Minting_
    -   _Public Burn_
    -   _Missing Requirements_
-   NFTGuard is also [extensible](https://github.com/enzymefinance/oyente/tree/master) for smart contracts with Solidity versions higher than _0.8.0_.

## Publication

NFTGuard and the datasets for defining NFT defects are proposed from the ISSTA'23 paper [Definition and Detection of Defects in NFT Smart Contracts](https://dl.acm.org/doi/10.1145/3597926.3598063).
