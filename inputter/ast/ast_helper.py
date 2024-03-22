import json

from cfg_builder.utils import run_command
from inputter.ast.ast_walker import AstWalker
from inputter.ast.safe_fun_walker import SafeFunWalker


class AstHelper:
    # scalability, method to its declaration id in AST
    # adapted to solidity 0.8.x
    method_to_ref_decl_ids = {}

    def __init__(self, filename, remap, input_type):
        self.input_type = input_type
        self.remap = remap
        self.filename = filename
        if input_type == "solidity":
            self.source_list = self.get_source_list(filename)
            self.storage_layouts = self.get_storage_layouts(filename)
        else:
            raise Exception("There is no such type of inputter")
        self.contracts = self.extract_contract_definitions(self.source_list)

    def get_source_list(self, filename):
        cmd = "solc --combined-json ast %s %s" % (
            filename,
            " ".join(self.remap),
        )
        out = run_command(cmd)
        out = json.loads(out)
        return out["sources"]

    def get_storage_layouts(self, filename):
        cmd = "solc --combined-json storage-layout %s %s" % (
            filename,
            " ".join(self.remap),
        )
        out = run_command(cmd)
        out = json.loads(out)
        return out["contracts"]

    def extract_contract_definitions(self, sourcesList):
        ret = {
            "contractsById": {},
            "contractsByName": {},
            "sourcesByContract": {},
        }
        walker = AstWalker()
        for k in sourcesList:
            if self.input_type == "solidity":
                ast = sourcesList[k]["AST"]
            else:
                # legacyAST deprecated
                ast = sourcesList[k]["legacyAST"]
            nodes = []
            walker.walk(ast, {"nodeType": "ContractDefinition"}, nodes)

            for node in nodes:
                ret["contractsById"][node["id"]] = node
                ret["sourcesByContract"][node["id"]] = k
                ret["contractsByName"][k + ":" + node["name"]] = node

        return ret

    def get_linearized_base_contracts(self, id, contractsById):
        return map(
            lambda id: contractsById[id], contractsById[id]["linearizedBaseContracts"]
        )

    def extract_state_definitions(self, c_name):
        node = self.contracts["contractsByName"][c_name]
        state_vars = []
        if node:
            base_contracts = self.get_linearized_base_contracts(
                node["id"], self.contracts["contractsById"]
            )
            base_contracts = list(base_contracts)
            base_contracts = list(reversed(base_contracts))
            for contract in base_contracts:
                if "nodes" in contract:
                    for item in contract["nodes"]:
                        if item["nodeType"] == "VariableDeclaration":
                            state_vars.append(item)
        return state_vars

    def extract_states_definitions(self):
        ret = {}

        for contract in self.contracts["contractsById"]:
            name = self.contracts["contractsById"][contract]["name"]
            source = self.contracts["sourcesByContract"][contract]
            full_name = source + ":" + name
            ret[full_name] = self.extract_state_definitions(full_name)
        return ret

    def extract_states_storage_layouts(self):
        ret = {}
        for contract in self.contracts["contractsById"]:
            name = self.contracts["contractsById"][contract]["name"]
            source = self.contracts["sourcesByContract"][contract]
            full_name = source + ":" + name
            ret[full_name] = self.extract_state_storage_layouts(full_name)
        return ret

    def extract_state_storage_layouts(self, c_name):
        node = self.storage_layouts[c_name]["storage-layout"]["storage"]
        id_to_state_vars = {}
        if node:
            for i in node:
                id_to_state_vars[i["astId"]] = i["slot"]
        return id_to_state_vars

    def extract_func_call_definitions(self, c_name):
        node = self.contracts["contractsByName"][c_name]
        walker = AstWalker()
        nodes = []
        if node:
            walker.walk(node, {"nodeType": "FunctionCall"}, nodes)
        return nodes

    def extract_safe_func_call_info(self, c_name):
        node = self.contracts["contractsByName"][c_name]
        walker = SafeFunWalker()
        if node:
            walker.walk_safe_fun(node)
        return walker.modifications_after_call

    def extract_func_calls_definitions(self):
        ret = {}
        for contract in self.contracts["contractsById"]:
            name = self.contracts["contractsById"][contract]["name"]
            source = self.contracts["sourcesByContract"][contract]
            full_name = source + ":" + name
            ret[full_name] = self.extract_func_call_definitions(full_name)
        return ret

    def extract_state_variable_names(self, c_name):
        state_variables = self.extract_states_definitions()[c_name]
        var_names = []
        for var_name in state_variables:
            var_names.append(var_name["name"])
        return var_names

    def extract_func_call_srcs(self, c_name):
        func_calls = self.extract_func_calls_definitions()[c_name]
        func_call_srcs = []
        for func_call in func_calls:
            func_call_srcs.append(func_call["src"])
        return func_call_srcs

    # for suicide/selfdestruct purpose
    # omit temporally
    def get_callee_src_pairs(self, c_name):
        node = self.contracts["contractsByName"][c_name]
        walker = AstWalker()
        nodes = []
        if node:
            list_of_attributes = [
                {"attributes": {"member_name": "delegatecall"}},
                {"attributes": {"member_name": "call"}},
                {"attributes": {"member_name": "callcode"}},
            ]
            walker.walk(node, list_of_attributes, nodes)

        callee_src_pairs = []
        for node in nodes:
            if "children" in node and node["children"]:
                type_of_first_child = node["children"][0]["attributes"]["type"]
                if type_of_first_child.split(" ")[0] == "contract":
                    contract = type_of_first_child.split(" ")[1]
                    contract_path = self._find_contract_path(
                        self.contracts["contractsByName"].keys(), contract
                    )
                    callee_src_pairs.append((contract_path, node["src"]))
        return callee_src_pairs

    def get_func_name_to_params(self, c_name):
        node = self.contracts["contractsByName"][c_name]
        walker = AstWalker()
        func_def_nodes = []
        if node:
            walker.walk(node, {"nodeType": "FunctionDefinition"}, func_def_nodes)

        func_name_to_params = {}
        for func_def_node in func_def_nodes:
            func_name = func_def_node["name"]

            params_nodes = []
            walker.walk(func_def_node, {"nodeType": "ParameterList"}, params_nodes)

            params_node = params_nodes[0]
            param_nodes = []
            walker.walk(params_node, {"nodeType": "VariableDeclaration"}, param_nodes)

            for param_node in param_nodes:
                var_name = param_node["name"]
                type_name = param_node["typeName"]["nodeType"]
                if type_name == "ArrayTypeName":
                    literal_nodes = []
                    walker.walk(param_node, {"nodeType": "Literal"}, literal_nodes)
                    if literal_nodes:
                        array_size = int(literal_nodes[0]["value"])
                    else:
                        array_size = 1
                    param = {"name": var_name, "type": type_name, "value": array_size}
                elif type_name == "ElementaryTypeName":
                    param = {"name": var_name, "type": type_name}
                else:
                    param = {"name": var_name, "type": type_name}

                if func_name not in func_name_to_params:
                    func_name_to_params[func_name] = [param]
                else:
                    func_name_to_params[func_name].append(param)
        return func_name_to_params

    def _find_contract_path(self, contract_paths, contract):
        for path in contract_paths:
            cname = path.split(":")[-1]
            if contract == cname:
                return path
        return ""
