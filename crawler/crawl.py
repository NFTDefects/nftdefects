import argparse
import json
import os
from time import sleep
import logging

import requests as rq


def make_dir(path):
    os.makedirs(path, exist_ok=True)


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError:
        return False
    return True


send_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    "Connection": "keep-alive",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


def crawl_contract(rootdir, c_address):
    root = rootdir
    contract_address = c_address
    # contract_name = row[2]
    api_key = os.getenv("ETHERSCAN_API_KEY")
    params = {"module": "contract", "action": "getsourcecode", "address": c_address}
    if api_key:
        params["apikey"] = api_key
    else:
        logging.warning("ETHERSCAN_API_KEY not set; proceeding without API key")
    output = rq.get("https://api.etherscan.io/api", headers=send_headers, params=params)

    # sleep to avoid ban
    sleep(2)
    json_res = output.json()
    if "result" in json_res:
        source_code = json_res["result"][0]["SourceCode"]
        make_dir(root + contract_address)
        if is_json(source_code):
            res = json.loads(source_code)
            for key in res:
                logging.debug(key)
                with open(root + contract_address + "/" + key, "w", encoding="UTF-8") as sol_file:
                    sol_file.write(res[key]["content"])
        elif source_code[0] == source_code[1] == "{":
            new_code = source_code[1:-1]
            res = json.loads(new_code)
            sources = res["sources"]
            for name in sources:
                logging.debug(name)
                _dir, _file = os.path.split(root + contract_address + "/" + name)
                logging.debug(_dir)
                make_dir(_dir)
                with open(root + contract_address + "/" + name, "w", encoding="UTF-8") as sol_file:
                    sol_file.write(sources[name]["content"])
        else:
            with open(
                root + contract_address + "/" + contract_address + ".sol",
                "w",
                encoding="UTF-8",
            ) as sol_file:
                sol_file.write(source_code)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dir", type=str, help="output crawled file path, end with '/'"
    )
    parser.add_argument("--caddress", type=str, help="contract address")
    args = parser.parse_args()
    crawl_contract(args.dir, args.caddress)
