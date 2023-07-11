#!/usr/bin/env python

import argparse
import logging
import re
import subprocess
import time
import six
import global_params
from cfg_builder import sym_exec
from cfg_builder.utils import run_command
from inputter.input_helper import InputHelper


def cmd_exists(cmd):
    """Check the command in system's PATH

    Args:
        cmd (_type_): given command

    Returns:
        bool: command installed or not
    """
    return (
        subprocess.call(
            "type " + cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        == 0
    )


def compare_versions(version1, version2):
    """Compare two given versions

    Args:
        version1 (_type_): one version
        version2 (_type_): the other version
    """

    def normalize(v):
        return [int(x) for x in re.sub(r"(\.0+)*$", "", v).split(".")]

    version1 = normalize(version1)
    version2 = normalize(version2)
    if six.PY2:
        return cmp(version1, version2)
    else:
        return (version1 > version2) - (version1 < version2)


def has_dependencies_installed():
    """Checks whether all the necessary dependencies are installed

    Returns:
        bool: whether dependencies are installed
    """
    try:
        import z3
        import z3.z3util

        z3_version = z3.get_version_string()
        tested_z3_version = "4.8.13"
        # if compare_versions(z3_version, tested_z3_version) > 0:
        #     logging.warning(
        #         "You are using an untested version of z3. %s is the officially tested version" % tested_z3_version)
    except e:
        logging.critical(e)
        logging.critical(
            "Z3 is not available. Please install z3 from https://github.com/Z3Prover/z3."
        )
        return False

    if not cmd_exists("evm"):
        logging.critical(
            "Please install evm from go-ethereum and make sure it is in the path."
        )
        return False
    else:
        cmd = "evm --version"
        out = run_command(cmd).strip()
        evm_version = re.findall(r"evm version (\d*.\d*.\d*)", out)[0]
        tested_evm_version = "1.10.21"
        if compare_versions(evm_version, tested_evm_version) > 0:
            logging.warning(
                "You are using evm version %s. The supported version is %s"
                % (evm_version, tested_evm_version)
            )

    if not cmd_exists("solc"):
        logging.critical(
            "solc is missing. Please install the solidity compiler and make sure solc is in the path."
        )
        return False
    else:
        cmd = "solc --version"
        out = run_command(cmd).strip()
        solc_version = re.findall(r"Version: (\d*.\d*.\d*)", out)[0]
        tested_solc_version = "0.8.16"
        if compare_versions(solc_version, tested_solc_version) > 0:
            logging.warning(
                "You are using solc version %s, The latest supported version is %s"
                % (solc_version, tested_solc_version)
            )

    return True


def run_solidity_analysis(inputs):
    """Run analysis for solidity input

    Args:
        inputs (_type_): input contracts

    Returns:
        _type_: analysis results and run status
    """
    results = {}
    exit_code = 0

    # for our tool, we must find some key features
    for inp in inputs:
        logging.info("contract %s:", inp["contract"])

        result, return_code = sym_exec.run(
            disasm_file=inp["disasm_file"],
            source_map=inp["source_map"],
            slot_map=inp["slot_map"],
            source_file=inp["source"],
        )

        try:
            c_source = inp["c_source"]
            c_name = inp["c_name"]
            results[c_source][c_name] = result
        except:
            results[c_source] = {c_name: result}

        if return_code == 1:
            exit_code = 1
    return results, exit_code


def analyze_solidity(input_type="solidity"):
    """entrance to analyze solidity and prepare MUST info from Inputter for feature_detector

    Args:
        input_type (str, optional): _description_. Defaults to 'solidity'.

    Returns:
        integer: exit status of the execution
    """
    global args

    if input_type == "solidity":
        helper = InputHelper(
            InputHelper.SOLIDITY,
            source=args.source,
            evm=args.evm,
            compilation_err=args.compilation_error,
        )
    else:
        return
    inputs = helper.get_inputs(global_params.TARGET_CONTRACTS)

    results, exit_code = run_solidity_analysis(inputs)
    helper.rm_tmp_files()

    return exit_code


def main():
    """Entrance for the analysis with input options"""
    # TODO: Implement -o switch.

    global args

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)

    # supported arguments refer to Oyente
    group.add_argument(
        "-s",
        "--source",
        type=str,
        help="local source file name. Solidity by default. Use -b to process evm instead. Use stdin to read from stdin.",
    )

    parser.add_argument(
        "-cnames",
        "--target-contracts",
        type=str,
        nargs="+",
        help="The name of targeted contracts. If specified, only the specified contracts in the source code will be processed. By default, all contracts in Solidity code are processed.",
    )

    parser.add_argument(
        "--version", action="version", version="NFTGuard version 0.1.0 - Boom"
    )

    parser.add_argument(
        "-t", "--timeout", help="Timeout for Z3 in ms.", action="store", type=int
    )
    parser.add_argument(
        "-gl",
        "--gaslimit",
        help="Limit Gas",
        action="store",
        dest="gas_limit",
        type=int,
    )
    parser.add_argument(
        "-ll",
        "--looplimit",
        help="Limit number of loops",
        action="store",
        dest="loop_limit",
        type=int,
    )
    parser.add_argument(
        "-dl",
        "--depthlimit",
        help="Limit DFS depth",
        action="store",
        dest="depth_limit",
        type=int,
    )

    parser.add_argument(
        "-glt",
        "--global-timeout",
        help="Timeout for symbolic execution",
        action="store",
        dest="global_timeout",
        type=int,
    )
    parser.add_argument(
        "-addr",
        "--address",
        help="Mark contract address in the json output (-j)",
        action="store",
        dest="address",
        type=str,
    )

    parser.add_argument(
        "-e", "--evm", help="Do not remove the .evm file.", action="store_true"
    )
    parser.add_argument(
        "-j", "--json", help="Redirect results to a json file.", action="store_true"
    )
    parser.add_argument(
        "-p", "--paths", help="Print path condition information.", action="store_true"
    )
    parser.add_argument(
        "-db", "--debug", help="Display debug information", action="store_true"
    )
    parser.add_argument(
        "-r", "--report", help="Create .report file.", action="store_true"
    )
    parser.add_argument(
        "-v", "--verbose", help="Verbose output, print everything.", action="store_true"
    )
    parser.add_argument(
        "-pl",
        "--parallel",
        help="Run NFTGuard in parallel. Note: The performance may depend on the contract",
        action="store_true",
    )
    parser.add_argument(
        "-ce",
        "--compilation-error",
        help="Display compilation errors",
        action="store_true",
    )
    parser.add_argument(
        "-gtc",
        "--generate-test-cases",
        help="Generate test cases each branch of symbolic execution tree",
        action="store_true",
    )

    args = parser.parse_args()

    if args.timeout:
        global_params.TIMEOUT = args.timeout

    logging.basicConfig()
    rootLogger = logging.getLogger(None)

    if args.verbose:
        rootLogger.setLevel(level=logging.DEBUG)
    else:
        rootLogger.setLevel(level=logging.INFO)

    global_params.PRINT_PATHS = 1 if args.paths else 0
    global_params.REPORT_MODE = 1 if args.report else 0

    global_params.STORE_RESULT = 1 if args.json else 0
    global_params.DEBUG_MODE = 1 if args.debug else 0
    global_params.GENERATE_TEST_CASES = 1 if args.generate_test_cases else 0
    global_params.PARALLEL = 1 if args.parallel else 0
    # for writing contract address
    if args.address:
        global_params.CONTRACT_ADDRESS = args.address

    global_params.TARGET_CONTRACTS = args.target_contracts

    global_params.SOURCE = args.source

    # set limit to set execution bounds
    if args.depth_limit:
        global_params.DEPTH_LIMIT = args.depth_limit
    if args.gas_limit:
        global_params.GAS_LIMIT = args.gas_limit
    if args.loop_limit:
        global_params.LOOP_LIMIT = args.loop_limit
    else:
        if args.global_timeout:
            global_params.GLOBAL_TIMEOUT = args.global_timeout

    if not has_dependencies_installed():
        return

    # analyze Solidity source code
    exit_code = analyze_solidity()

    exit(exit_code)


if __name__ == "__main__":
    main()
