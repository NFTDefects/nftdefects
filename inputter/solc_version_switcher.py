import re
import subprocess
import logging


def install_and_use_solc_version(version_info):
    installed_versions_output = subprocess.check_output(
        ["solc-select", "versions"]
    ).decode()

    if version_info in installed_versions_output:
        logging.info(f"Version {version_info} is already installed.")
    else:
        logging.info(f"Installing version {version_info}...")
        subprocess.run(["solc-select", "install", version_info], check=True)
        logging.info(f"Version {version_info} installed successfully.")
    # else:
    #     raise ValueError(f"Version {version_info} is not available for installation.")

    subprocess.run(["solc-select", "use", version_info], check=True)
    logging.info(f"Switched to version {version_info}.")


class SolidityVersionSwitcher:
    def __init__(self, target_path):
        self.target = target_path

    def load_solidity_code(self):
        with open(self.target, "r") as file:
            solidity_code = file.read()
        return solidity_code

    def extract_solidity_version(self, solidity_code):
        version_match = re.search(r"pragma\s+solidity\s+([^;]+);", solidity_code)
        if version_match:
            version_info = version_match.group(1)
            version_info = version_info.replace("^", "")
            return version_info
        else:
            raise ValueError("Solidity version directive not found in the code.")

    def switch_solc_version(self, version_info):
        try:
            subprocess.run(["solc-select", "use", version_info], check=True)
            logging.info(f"Successfully switched to Solidity version {version_info}.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to switch to Solidity version {version_info}. Error: {e}")

    def run(self):
        solidity_code = self.load_solidity_code()
        version_info = self.extract_solidity_version(solidity_code)
        install_and_use_solc_version(version_info)
