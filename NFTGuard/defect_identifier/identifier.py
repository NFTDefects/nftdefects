import time
import global_params
import json
import logging
from rich.console import Console
from rich.table import Table
from defect_identifier.defect import PublicBurnDefect, ReentrancyDefect, RiskyProxyDefect, UnlimitedMintingDefect, ViolationDefect

log = logging.getLogger(__name__)


class Identifier:
    @classmethod
    def detect_defects(self, instructions, results, g_src_map, visited_pcs, global_problematic_pcs, begin, g_disasm_file):
        if instructions:
            evm_code_coverage = float(len(visited_pcs)) / \
                len(instructions.keys()) * 100
            # log.info("\t  EVM Code Coverage: \t\t\t %s%%",
            #          round(evm_code_coverage, 1))
            results["evm_code_coverage"] = str(round(evm_code_coverage, 1))
            results["instructions"] = str(len(instructions.keys()))

            end = time.time()

            # *All Defects to be detectd...
            self.detect_violation(self, results, g_src_map,
                                  global_problematic_pcs)
            self.detect_reentrancy(
                self, results, g_src_map, global_problematic_pcs)
            self.detect_proxy(self, results, g_src_map, global_problematic_pcs)
            self.detect_unlimited_minting(
                self, results, g_src_map, global_problematic_pcs)
            self.detect_public_burn(
                self, results, g_src_map, global_problematic_pcs)

            defect_table = Table()

            defect_table.add_column("Defect", justify="right",
                                    style="dim", no_wrap=True)
            defect_table.add_column("Status", style="green")
            defect_table.add_column(
                "Location", justify="left", style="cyan")

            defect_table.add_row("Risky Mutable Proxy",
                                 str(proxy.is_defective()), str(proxy))
            defect_table.add_row("ERC-721 Re-entrancy",
                                 str(reentrancy.is_defective()), str(reentrancy))
            defect_table.add_row("Unlimited Minting",
                                 str(unlimited_minting.is_defective()), str(unlimited_minting))
            defect_table.add_row("Missing Requirements", str(violation.is_defective()),
                                 str(violation))
            defect_table.add_row("Public Burn", str(public_burn.is_defective()),
                                 str(public_burn))

            param_table = Table()
            param_table.add_column("Time", justify="left",
                                   style="cyan", no_wrap=True)
            param_table.add_column("Coverage", justify="left",
                                   style="yellow", no_wrap=True)
            param_table.add_row(str(round(end - begin, 1)),
                                str(round(evm_code_coverage, 1)))

            reporter = Table(title="NFTGuard GENESIS v0.0.1")
            reporter.add_column("Defect Detection", justify="left")
            reporter.add_column("Execution States", justify="left")
            reporter.add_row(defect_table, param_table)

            console = Console()
            console.print(reporter)

            # if g_src_map:
            #     self.log_info()

        else:
            log.info("\t  No Instructions \t")
            results["evm_code_coverage"] = "0/0"
        self.closing_message(begin, g_disasm_file, results, end)
        return results, self.defect_found(g_src_map)

    def detect_violation(self, results, g_src_map, global_problematic_pcs):
        global violation

        pcs = global_problematic_pcs["violation_defect"]
        violation = ViolationDefect(g_src_map, pcs)

        if g_src_map:
            results['analysis']['violation'] = violation.get_warnings()
        else:
            results['analysis']['violation'] = violation.is_defective()
        results['bool_defect']['violation'] = violation.is_defective()
        # log.info("\t  Standard Violation Defect: \t\t %s",
        #          violation.is_defective())

    def detect_reentrancy(self, results, g_src_map, global_problematic_pcs):
        global reentrancy

        pcs = global_problematic_pcs["reentrancy_defect"]
        reentrancy = ReentrancyDefect(g_src_map, pcs)

        if g_src_map:
            results['analysis']['reentrancy'] = reentrancy.get_warnings()
        else:
            results['analysis']['reentrancy'] = reentrancy.is_defective()

        results['bool_defect']['reentrancy'] = reentrancy.is_defective()
        # log.info("\t  ERC721-Reentrancy Defect: \t\t %s",
        #          reentrancy.is_defective())

    def detect_proxy(self, results, g_src_map, global_problematic_pcs):
        global proxy

        pcs = global_problematic_pcs["proxy_defect"]
        proxy = RiskyProxyDefect(g_src_map, pcs)

        if g_src_map:
            results['analysis']['proxy'] = proxy.get_warnings()
        else:
            results['analysis']['proxy'] = proxy.is_defective()
        results["bool_defect"]["proxy"] = proxy.is_defective()
        # log.info("\t  Risky Mutable Proxy Defect: \t\t %s",
        #          proxy.is_defective())

    def detect_unlimited_minting(self, results, g_src_map, global_problematic_pcs):
        global unlimited_minting

        pcs = global_problematic_pcs["unlimited_minting_defect"]
        unlimited_minting = UnlimitedMintingDefect(g_src_map, pcs)

        if g_src_map:
            results['analysis']['unlimited_minting'] = unlimited_minting.get_warnings()
        else:
            results['analysis']['unlimited_minting'] = unlimited_minting.is_defective()
        results["bool_defect"]["unlimited_minting"] = unlimited_minting.is_defective()
        # log.info("\t  Unlimited Minting Defect: \t\t %s",
        #          unlimited_minting.is_defective())

    def detect_public_burn(self, results, g_src_map, global_problematic_pcs):
        global public_burn

        pcs = global_problematic_pcs["burn_defect"]
        public_burn = PublicBurnDefect(g_src_map, pcs)

        if g_src_map:
            results['analysis']['burn'] = public_burn.get_warnings()
        else:
            results['analysis']['burn'] = public_burn.is_defective()
        results["bool_defect"]["burn"] = public_burn.is_defective()
        # log.info("\t  Public Burn Defect: \t\t\t %s",
        #          public_burn.is_defective())

    def log_info():
        global reentrancy
        global violation
        global proxy
        global unlimited_minting
        global public_burn

        defects = [reentrancy, violation, proxy,
                   unlimited_minting, public_burn]

        for defect in defects:
            s = str(defect)
            if s:
                log.info(s)

    def defect_found(g_src_map):
        global reentrancy
        global violation
        global proxy
        global unlimited_minting
        global public_burn

        defects = [reentrancy, violation, proxy,
                   unlimited_minting, public_burn]

        for defect in defects:
            if defect.is_defective():
                return 1
        return 0

    def closing_message(begin, g_disasm_file, results, end):

        results["time"] = str(end - begin)
        # write down extra contract info...
        results["address"] = global_params.CONTRACT_ADDRESS
        results["contract_count"] = global_params.CONTRACT_COUNT
        results["storage_var_count"] = global_params.STORAGE_VAR_COUNT
        results["sload_count"] = global_params.SLOAD_COUNT
        results["sstore_count"] = global_params.SSTORE_COUNT
        results["keccak256_count"] = global_params.KECCAK256_COUNT
        results["pub_fun_count"] = global_params.PUB_FUN_COUNT

        log.info("\t====== Analysis Completed ======")
        if global_params.STORE_RESULT:
            result_file = g_disasm_file.split('.evm.disasm')[0] + '.json'
            with open(result_file, 'w') as of:
                of.write(json.dumps(results, indent=1))
            log.info("Wrote results to %s.", result_file)
