import time
import global_params
import json
import logging
from typing import Dict, Any, Tuple
from defect_identifier.registry import DefectRegistry
from reporting.reporter import AnalysisReporter

log = logging.getLogger(__name__)


class AnalysisContext:
    """Context object for passing analysis parameters."""
    
    def __init__(self, instructions=None, g_src_map=None, visited_pcs=None,
                 global_problematic_pcs=None, begin_time=None, g_disasm_file=None):
        self.instructions = instructions
        self.g_src_map = g_src_map
        self.visited_pcs = visited_pcs or set()
        self.global_problematic_pcs = global_problematic_pcs or {}
        self.begin_time = begin_time or time.time()
        self.g_disasm_file = g_disasm_file


class Identifier:
    """Main class for defect identification and analysis coordination."""
    
    def __init__(self):
        self.registry = DefectRegistry()
        self.reporter = AnalysisReporter()
    
    @classmethod 
    def detect_defects(
        cls,
        instructions,
        results,
        g_src_map,
        visited_pcs,
        global_problematic_pcs,
        begin,
        g_disasm_file,
    ) -> Tuple[Dict[str, Any], int]:
        """Analyzes defects and reports the final results."""
        identifier = cls()
        return identifier._run_analysis(
            instructions, results, g_src_map, visited_pcs,
            global_problematic_pcs, begin, g_disasm_file
        )
    
    def _run_analysis(
        self,
        instructions,
        results,
        g_src_map,
        visited_pcs,
        global_problematic_pcs,
        begin,
        g_disasm_file,
    ) -> Tuple[Dict[str, Any], int]:
        """Internal method to run the complete analysis."""
        end = time.time()
        
        if instructions:
            # Calculate coverage statistics
            evm_code_coverage = float(len(visited_pcs)) / len(instructions.keys()) * 100
            results["evm_code_coverage"] = str(round(evm_code_coverage, 1))
            results["instructions"] = str(len(instructions.keys()))
            
            # Run defect detection using registry
            detection_results = self.registry.detect_all(g_src_map, global_problematic_pcs)
            
            # Update results with detection information
            self._update_results_with_detections(results, detection_results, g_src_map)
            
            # Create analysis statistics
            analysis_stats = {
                'execution_time': end - begin,
                'evm_code_coverage': round(evm_code_coverage, 1),
                'instructions': len(instructions.keys())
            }
            
            # Print final report
            self.reporter.print_final_report(self.registry, analysis_stats)
            self.reporter.log_defect_summary(self.registry)
            
        else:
            log.info("\t  No Instructions \t")
            results["evm_code_coverage"] = "0/0"
            
        self._finalize_results(begin, g_disasm_file, results, end)
        return results, self._get_exit_code()
    
    def _update_results_with_detections(self, results: Dict[str, Any], 
                                       detection_results: Dict[str, Any], 
                                       g_src_map) -> None:
        """Update results dictionary with detection information."""
        if "analysis" not in results:
            results["analysis"] = {}
        if "bool_defect" not in results:
            results["bool_defect"] = {}
            
        # Map detector names to result keys
        key_mapping = {
            "ERC721 Standard Violation": "violation",
            "ERC721 Reentrancy": "reentrancy",
            "Risky Mutable Proxy": "proxy", 
            "Unlimited Minting": "unlimited_minting",
            "Public Burn": "burn"
        }
        
        for detector_name, result in detection_results.items():
            key = key_mapping.get(detector_name, detector_name.lower().replace(" ", "_"))
            
            if g_src_map:
                results["analysis"][key] = result.warnings
            else:
                results["analysis"][key] = result.is_defective
                
            results["bool_defect"][key] = result.is_defective
    
    def _get_exit_code(self) -> int:
        """Get exit code based on detection results."""
        return 1 if self.registry.has_any_defects() else 0

    # Legacy methods removed - functionality moved to DefectRegistry

    def _finalize_results(self, begin, g_disasm_file, results, end):
        """Finalize analysis results and save to file if requested."""
        results["time"] = str(end - begin)
        # write down extra contract info...
        results["address"] = global_params.CONTRACT_ADDRESS
        results["contract_count"] = global_params.CONTRACT_COUNT
        results["storage_var_count"] = global_params.STORAGE_VAR_COUNT
        results["pub_fun_count"] = global_params.PUB_FUN_COUNT

        log.info("\t====== Analysis Completed ======")
        if global_params.STORE_RESULT:
            result_file = g_disasm_file.split(".evm.disasm")[0] + ".json"
            try:
                with open(result_file, "w") as of:
                    of.write(json.dumps(results, indent=1))
                log.info("Wrote results to %s.", result_file)
            except IOError as e:
                log.error(f"Failed to write results to {result_file}: {e}")
