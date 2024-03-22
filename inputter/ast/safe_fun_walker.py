def find_referenced_declaration_values(node):
    referenced_declarations = []

    def recurse(current_node):
        if isinstance(current_node, dict):
            if "name" in current_node:
                referenced_declarations.append(current_node["name"])
            for value in current_node.values():
                recurse(value)
        elif isinstance(current_node, list):
            for item in current_node:
                recurse(item)

    recurse(node)
    return referenced_declarations


class SafeFunWalker:
    def __init__(self):
        self.found_function_call = False
        self.call_loc = ""
        self.modifications_after_call = []

    def walk(self, node, attributes, nodes):
        if isinstance(attributes, dict):
            self._walk_with_attrs(node, attributes, nodes)

    def _walk_with_attrs(self, node, attributes, nodes):
        if self._check_attributes(node, attributes):
            nodes.append(node)
        else:
            if isinstance(node, dict):
                for key in node:
                    if isinstance(node[key], list):
                        for child in node[key]:
                            self._walk_with_attrs(child, attributes, nodes)
                    elif isinstance(node[key], dict):
                        self._walk_with_attrs(node[key], attributes, nodes)
                    else:
                        continue
            elif isinstance(node, list):
                for key in node:
                    self._walk_with_attrs(node[key], attributes, nodes)

    def walk_safe_fun(self, node):
        nodes = []
        found_function_call = False
        call_loc = []
        modifications_after_call = []
        self.walk(node, {"nodeType": "FunctionDefinition"}, nodes)
        for i in range(len(nodes)):
            if "body" in nodes[i].keys():
                if "statements" in nodes[i]["body"].keys():
                    for statement in nodes[i]["body"]["statements"]:
                        if found_function_call:
                            if (
                                statement.get("nodeType") == "ExpressionStatement"
                                and statement.get("expression", {}).get("nodeType")
                                == "Assignment"
                            ):
                                modifications_after_call.append(
                                    {
                                        call_loc[0]: find_referenced_declaration_values(
                                            statement
                                        )
                                    }
                                )
                        else:
                            node_safe_mint = []
                            node_safe_transfer = []
                            self.walk(statement, {"name": "_safeMint"}, node_safe_mint)
                            self.walk(
                                statement,
                                {"name": "safeTransferFrom"},
                                node_safe_transfer,
                            )
                            if len(node_safe_mint):
                                found_function_call = True
                            for node in node_safe_mint:
                                call_loc.append(node["src"])
                            continue

                    if len(modifications_after_call) != 0:
                        self.modifications_after_call = modifications_after_call
                    call_loc = []
                    found_function_call = False

    def _check_attributes(self, node, attributes):
        if not isinstance(node, dict):
            return False
        for name in attributes:
            if isinstance(attributes[name], str):
                if name not in node or attributes[name] != node[name]:
                    return False
            elif name not in node or node[name] != attributes[name]:
                return False
        return True

    def _check_list_of_attributes(self, node, list_of_attributes):
        for attrs in list_of_attributes:
            if self._check_attributes(node, attrs):
                return True
        return False
