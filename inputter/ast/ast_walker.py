class AstWalker:
    def walk(self, node, attributes, nodes):
        if isinstance(attributes, dict):
            self._walk_with_attrs(node, attributes, nodes)
        else:
            self._walk_with_list_of_attrs(node, attributes, nodes)

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

    def _walk_with_list_of_attrs(self, node, list_of_attributes, nodes):
        if self._check_list_of_attributes(node, list_of_attributes):
            nodes.append(node)
        else:
            if isinstance(node, dict):
                for key in node:
                    if isinstance(node[key], list):
                        for child in node[key]:
                            self._walk_with_list_of_attrs(
                                child, list_of_attributes, nodes
                            )
                    elif isinstance(node[key], dict):
                        self._walk_with_list_of_attrs(
                            node[key], list_of_attributes, nodes
                        )
                    else:
                        continue
            elif isinstance(node, list):
                for key in node:
                    self._walk_with_list_of_attrs(node[key], list_of_attributes, nodes)

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
