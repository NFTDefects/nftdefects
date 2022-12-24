import re


def calculate_slot(id_to_state_vars):
    # TODO calculate slot id of state vars
    slot_id = 0
    bit_remain = 256
    simpler_slot_map = {}
    name_to_type = {}
    for id in id_to_state_vars:
        for key in id_to_state_vars[id]:
            constant = id_to_state_vars[id][key]['constant']
            mutable = id_to_state_vars[id][key]['mutability']
            type = id_to_state_vars[id][key]['type']
            name_to_type[key] = type
            neg = 0

            if constant or mutable == "immutable":
                id_to_state_vars[id][key]["slot_id"] = None
                continue
            if type == "address":
                neg = 160
            elif type == "bool":
                neg = 1
            elif type == "string":
                neg = 256
            elif len(re.findall('mapping(.*)', type)) > 0:
                neg = 256
            elif type.startswith("uint"):
                if re.findall('\d+', type):
                    neg = int(re.findall('\d+', type)[0])
                else:
                    neg = 256
            elif type.startswith("bytes"):
                if re.findall('\d+', type):
                    neg = int(re.findall('\d+', type)[0]) * 8
                else:
                    neg = 256
            elif len(re.findall('(.*)\[(.*?)\]', type)) > 0:
                neg = 256
            elif type.startswith("struct"):
                neg = 256

            if bit_remain - neg < 0:
                # new_slot = True
                slot_id += 1
                bit_remain = 256
            bit_remain = bit_remain - neg
            id_to_state_vars[id][key]["slot_id"] = slot_id
            if slot_id in simpler_slot_map:
                simpler_slot_map[slot_id].append({key: type})
            else:
                simpler_slot_map[slot_id] = [key]
    return id_to_state_vars, simpler_slot_map, name_to_type


def match_owner(id_to_state_vars, slot_map):
    # usually _owners, _tokenApprovals, _operatorApprovals, _ownerships, etc.
    keywords = 'OWNER'
    index = []
    for id in id_to_state_vars:
        for key in id_to_state_vars[id]:
            if any([w in key.upper() and w for w in keywords.split(',')]):
                if slot_map[id][key]["slot_id"] is not None:
                    index.append(slot_map[id][key]["slot_id"])
    return index


def match_approval(id_to_state_vars, slot_map):
    # usually _owners, _tokenApprovals, _operatorApprovals, _ownerships, etc.
    keywords = 'APPROVAL,OPERATOR'
    index = []
    for id in id_to_state_vars:
        for key in id_to_state_vars[id]:
            if any([w in key.upper() and w for w in keywords.split(',')]):
                if slot_map[id][key]["slot_id"] is not None:
                    index.append(slot_map[id][key]["slot_id"])
    return index


def match_supply(id_to_state_vars, slot_map):
    # usually MAX_SUPPLY, _TOTALSUPPLY, MAX_TOKENS, etc.
    # *Add others: nextToken, totalMinted
    # seperate to prefix and suffix
    keywords_prefix = 'ALL,MAX,TOTAL,CURRENT,NEXT,TOTAL,TOKEN'
    keywords_suffix = 'TOKEN,SUPPLY,INDEX,MINTED'
    whole = 'COUNTER,SUPPLY,MINTCOUNT'
    index = []
    for id in id_to_state_vars:
        for key in id_to_state_vars[id]:
            # match prefix
            if any([w in key.upper() and w for w in keywords_prefix.split(',')]):
                # match suffix
                if any([w in key.upper() and w for w in keywords_suffix.split(',')]):
                    if slot_map[id][key]["slot_id"] is not None:
                        index.append(slot_map[id][key]["slot_id"])

    for id in id_to_state_vars:
        for key in id_to_state_vars[id]:
            if any(w in key.upper() and w for w in whole.split(',')):
                if slot_map[id][key]["slot_id"] is not None:
                    index.append(slot_map[id][key]["slot_id"])
    return index


def match_proxy(id_to_state_vars, slot_map):
    # should find address type vars
    keywords_prefix = 'PROXY'
    keywords_suffix = 'REGISTRY'
    index = []
    for id in id_to_state_vars:
        for key in id_to_state_vars[id]:
            # match prefix
            if any([w in key.upper() and w for w in keywords_prefix.split(',')]):
                # match suffix
                if any([w in key.upper() and w for w in keywords_suffix.split(',')]):
                    if slot_map[id][key]["slot_id"] is not None and slot_map[id][key]["type"] == "address":
                        index.append(slot_map[id][key]["slot_id"])
    return index
