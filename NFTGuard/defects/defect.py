import re


class Defect:
    def __init__(self, source_map, pcs):
        self.source_map = source_map
        self.pcs = self._rm_general_false_positives(pcs)
        if source_map:
            self.warnings = self._warnings()

    def is_defective(self):
        return bool(self.pcs)

    def get_warnings(self):
        return self.warnings

    def _rm_general_false_positives(self, pcs):
        new_pcs = pcs
        if self.source_map:
            new_pcs = self._rm_pcs_having_no_source_code(new_pcs)
            new_pcs = self._reduce_pcs_having_the_same_pos(new_pcs)
        return new_pcs

    def _rm_pcs_having_no_source_code(self, pcs):
        return [pc for pc in pcs if self.source_map.get_source_code(pc)]

    def _reduce_pcs_having_the_same_pos(self, pcs):
        d = {}
        for pc in pcs:
            pos = str(self.source_map.instr_positions[pc])
            if pos not in d:
                d[pos] = pc
        return d.values()

    def _warnings(self):
        warnings = []
        for pc in self.pcs:
            source_code = self.source_map.get_source_code(pc)
            if not source_code:
                continue

            source_code = self.source_map.get_buggy_line(pc)
            s = self._warning_content(pc, source_code)
            if s:
                warnings.append(s)
        return warnings

    def _warning_content(self, pc, source_code):
        new_line_idx = source_code.find('\n')
        source_code = source_code.split('\n', 1)[0]
        location = self.source_map.get_location(pc)

        source = re.sub(self.source_map.root_path, '', self.source_map.get_filename())
        line = location['begin']['line'] + 1
        column = location['begin']['column'] + 1
        s = '%s:%s:%s: Warning: %s.\n' % (source, line, column, self.name)
        s += source_code
        if new_line_idx != -1:
            s += '\n' + self._leading_spaces(source_code) + '^\n'
            s += 'Spanning multiple lines.'
        return s

    def _leading_spaces(self, s):
        stripped_s = s.lstrip('[ \t]')
        len_of_leading_spaces = len(s) - len(stripped_s)
        return s[0:len_of_leading_spaces]

    def __str__(self):
        s = ''
        for warning in self.warnings:
            s += '\n' + warning
        return s.lstrip('\n')


class ViolationDefect(Defect):
    def __init__(self, source_map, pcs):
        self.name = 'ERC721 Standard Violation Defect'
        Defect.__init__(self, source_map, pcs)


class ReentrancyDefect(Defect):
    def __init__(self, source_map, pcs):
        self.name = 'ERC721 Reentrancy Defect'
        Defect.__init__(self, source_map, pcs)


class RiskyProxyDefect(Defect):
    def __init__(self, source_map, pcs):
        self.name = 'Risky Mutable Proxy Defect'
        Defect.__init__(self, source_map, pcs)


class UnlimitedMintingDefect(Defect):
    def __init__(self, source_map, pcs):
        self.name = 'Unlimited Minting Defect'
        Defect.__init__(self, source_map, pcs)


class PublicBurnDefect(Defect):
    def __init__(self, source_map, pcs):
        self.name = 'Public Burn Defect'
        Defect.__init__(self, source_map, pcs)
