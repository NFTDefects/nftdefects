import re
import logging

from inputter.ast.ast_helper import AstHelper


class SlotMap:

    ref_id_to_state_vars = {}
    parent_filename = ""
    slot_map = []
    simpler_slot_map = []
    name_to_type = []
    ast_helper = None
    # heuristic keyword matching
    owner_index = None
    approval_index = None
    supply_index = None
    proxy_index = None

    def __init__(
        self, cname, parent_filename, remap, input_type="solidity", root_path=""
    ):
        self.root_path = root_path
        self.cname = cname
        if not SlotMap.parent_filename:
            SlotMap.parent_filename = parent_filename
            if input_type == "solidity":
                SlotMap.ast_helper = AstHelper(
                    SlotMap.parent_filename, remap, input_type
                )
            else:
                # TODO add more type of inputter
                raise Exception("There is no such type of inputter")
            # extension of AST feature_detector (e.g., ref id in AST => {var name => type, immutabily, const, etc.})
            self.state_def = self.ast_helper.extract_states_definitions()
            self.ref_id_to_state_vars = self._get_ref_id_to_state_vars()
            self.ref_id_to_slot_id = self.ast_helper.extract_states_storage_layouts()[
                self.cname
            ]

            # name_to_type: mark var name => type
            # simpler_slot_map: mark var slot id
            (
                self.slot_map,
                self.simpler_slot_map,
                self.name_to_type,
            ) = self.calculate_slot()

            # new Solidity version support slot id output
            # solc --combined-json storage-layout ...
            # for this case, use the following code for extracting slots
            # (
            #     self.slot_map,
            #     self.simpler_slot_map,
            #     self.name_to_type,
            # ) = self.calculate_extracted_slot()

            # simple and heuristic keyword-matching strategy (extensible and to be refined)
            self.owner_index = self.match_owner()
            self.approval_index = self.match_approval()
            self.supply_index = self.match_supply()
            self.proxy_index = self.match_proxy()

    def _get_ref_id_to_state_vars(self):
        """GENESIS: get var dict (name => type). TODO need update

        Returns:
            mapping: a map from the var name to its type
        """
        state_vars = self.state_def[self.cname]
        var_dict = {}
        for state_v in state_vars:
            var_dict[state_v["id"]] = {
                state_v["name"]: {
                    "type": state_v["typeDescriptions"]["typeString"],
                    "constant": state_v["constant"],
                    "mutability": state_v["mutability"],
                }
            }
        return var_dict

    # def _get_compiler_version(self):

    def calculate_extracted_slot(self):
        """
        Calculates the extracted slot for each state variable.

        Returns:
            Tuple: A tuple containing the following:
                - id_to_state_vars (dict): A dictionary mapping IDs to state variables.
                - simpler_slot_map (dict): A simplified slot map.
                - name_to_type (dict): A dictionary mapping variable names to their types.
        """
        id_to_state_vars = self.ref_id_to_state_vars
        slots = self.ref_id_to_slot_id
        simpler_slot_map = {}
        name_to_type = {}
        for id in id_to_state_vars:
            for key in id_to_state_vars[id]:
                constant = id_to_state_vars[id][key]["constant"]
                mutable = id_to_state_vars[id][key]["mutability"]
                type = id_to_state_vars[id][key]["type"]
                name_to_type[key] = type
                if id in slots:
                    id_to_state_vars[id][key]["slot_id"] = slots[id]
                else:
                    id_to_state_vars[id][key]["slot_id"] = None

                if slots[id] in simpler_slot_map:
                    simpler_slot_map[slots[id]].append({key: type})
                else:
                    simpler_slot_map[slots[id]] = [key]
        logging.debug(simpler_slot_map)
        return id_to_state_vars, simpler_slot_map, name_to_type

    def calculate_slot(self):
        id_to_state_vars = self.ref_id_to_state_vars
        slot_id = 0
        bit_remain = 256
        simpler_slot_map = {}
        name_to_type = {}
        for id in id_to_state_vars:
            for key in id_to_state_vars[id]:
                constant = id_to_state_vars[id][key]["constant"]
                mutable = id_to_state_vars[id][key]["mutability"]
                type = id_to_state_vars[id][key]["type"]
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
                elif len(re.findall("mapping(.*)", type)) > 0:
                    neg = 256
                elif type.startswith("uint"):
                    if re.findall("\d+", type):
                        neg = int(re.findall("\d+", type)[0])
                    else:
                        neg = 256
                elif type.startswith("bytes"):
                    if re.findall("\d+", type):
                        neg = int(re.findall("\d+", type)[0]) * 8
                    else:
                        neg = 256
                elif len(re.findall("(.*)\[(.*?)\]", type)) > 0:
                    neg = 256
                elif type.startswith("struct"):
                    neg = 256

                if bit_remain - neg < 0:
                    slot_id += 1
                    bit_remain = 256
                bit_remain = bit_remain - neg
                id_to_state_vars[id][key]["slot_id"] = slot_id
                if slot_id in simpler_slot_map:
                    simpler_slot_map[slot_id].append({key: type})
                else:
                    simpler_slot_map[slot_id] = [key]
        return id_to_state_vars, simpler_slot_map, name_to_type

    def match_owner(self):
        """
        Returns a list of slot IDs that match the owner keywords in the state variables.

        Returns:
            list: A list of slot IDs.
        """
        id_to_state_vars = self._get_ref_id_to_state_vars()
        slot_map = self.slot_map
        # for _owners, _tokenApprovals, _operatorApprovals, _ownerships, etc.
        keywords = "OWNER"
        index = []
        for id in id_to_state_vars:
            for key in id_to_state_vars[id]:
                if any([w in key.upper() and w for w in keywords.split(",")]):
                    if slot_map[id][key]["slot_id"] is not None:
                        index.append(slot_map[id][key]["slot_id"])
        return index

    def match_approval(self):
        """
        Returns a list of slot IDs that correspond to state variables related to approvals.

        Returns:
            list: A list of slot IDs.
        """
        id_to_state_vars = self._get_ref_id_to_state_vars()
        slot_map = self.slot_map
        # for _owners, _tokenApprovals, _operatorApprovals, _ownerships, etc.
        keywords = "APPROVAL,OPERATOR"
        index = []
        for id in id_to_state_vars:
            for key in id_to_state_vars[id]:
                if any([w in key.upper() and w for w in keywords.split(",")]):
                    if slot_map[id][key]["slot_id"] is not None:
                        index.append(slot_map[id][key]["slot_id"])
        return index

    def match_supply(self):
        """
        Matches the supply-related state variables in the slot map and returns their corresponding slot IDs.

        Returns:
            list: A list of slot IDs corresponding to the supply-related state variables.
        """
        id_to_state_vars = self._get_ref_id_to_state_vars()
        slot_map = self.slot_map
        # for max_supply, _totalsupply, max_tokens, nextToken, totalMinted

        # seperate to prefix and suffix
        keywords_prefix = "ALL,MAX,TOTAL,CURRENT,NEXT,TOTAL,TOKEN"
        keywords_suffix = "TOKEN,SUPPLY,INDEX,MINTED"
        whole = "COUNTER,SUPPLY,MINTCOUNT"
        index = []
        for id in id_to_state_vars:
            for key in id_to_state_vars[id]:
                # match prefix
                if any([w in key.upper() and w for w in keywords_prefix.split(",")]):
                    # match suffix
                    if any(
                        [w in key.upper() and w for w in keywords_suffix.split(",")]
                    ):
                        if slot_map[id][key]["slot_id"] is not None:
                            index.append(slot_map[id][key]["slot_id"])

        for id in id_to_state_vars:
            for key in id_to_state_vars[id]:
                if any(w in key.upper() and w for w in whole.split(",")):
                    if slot_map[id][key]["slot_id"] is not None:
                        index.append(slot_map[id][key]["slot_id"])
        return index

    def match_proxy(self):
        """
        Finds the slot IDs of address type variables that match the specified keywords.

        Returns:
            list: A list of slot IDs.
        """
        id_to_state_vars = self._get_ref_id_to_state_vars()
        slot_map = self.slot_map
        # should find address type vars
        keywords_prefix = "PROXY"
        keywords_suffix = "REGISTRY"
        index = []
        for id in id_to_state_vars:
            for key in id_to_state_vars[id]:
                # match prefix
                if any([w in key.upper() and w for w in keywords_prefix.split(",")]):
                    # match suffix
                    if any(
                        [w in key.upper() and w for w in keywords_suffix.split(",")]
                    ):
                        if (
                            slot_map[id][key]["slot_id"] is not None
                            and slot_map[id][key]["type"] == "address"
                        ):
                            index.append(slot_map[id][key]["slot_id"])
        return index
