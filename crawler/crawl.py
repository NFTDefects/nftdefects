import argparse
import json
import os
from time import sleep

import requests as rq


def make_dir(path):
    folders = []
    while not os.path.isdir(path):
        path, suffix = os.path.split(path)
        folders.append(suffix)
    for folder in folders[::-1]:
        path = os.path.join(path, folder)
        os.mkdir(path)


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
    curl_link = (
        "https://api.etherscan.io/api?module=contract&action=getsourcecode&address="
        + c_address
        + "&apikey=HPB1MEZ5YEJ7GZJF7ASQDJ4MPU7YEUTIUT"
    )
    print(curl_link)

    output = rq.get(curl_link, headers=send_headers)

    # sleep to avoid ban
    sleep(2)
    json_res = output.json()
    if "result" in json_res:
        source_code = json_res["result"][0]["SourceCode"]
        make_dir(root + contract_address)
        if is_json(source_code):
            res = json.loads(source_code)
            for key in res:
                print(key)
                sol_file = open(
                    root + contract_address + "/" + key, "w", encoding="UTF-8"
                )
                sol_file.write(res[key]["content"])
                sol_file.close()
        elif source_code[0] == source_code[1] == "{":
            new_code = source_code[1:-1]
            res = json.loads(new_code)
            sources = res["sources"]
            for name in sources:
                print(name)
                _dir, _file = os.path.split(root + contract_address + "/" + name)
                print(_dir)
                make_dir(_dir)
                sol_file = open(
                    root + contract_address + "/" + name, "w", encoding="UTF-8"
                )
                sol_file.write(sources[name]["content"])
                sol_file.close()
        else:
            sol_file = open(
                root + contract_address + "/" + contract_address + ".sol",
                "w",
                encoding="UTF-8",
            )
            sol_file.write(source_code)
            sol_file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dir", type=str, help="output crawled file path, end with '/'"
    )
    parser.add_argument("--caddress", type=str, help="contract address")
    args = parser.parse_args()
    crawl_contract(args.dir, args.caddress)
