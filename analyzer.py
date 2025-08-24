"""Modern analyzer facade providing clean API for symbolic execution."""

import logging
import time
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from .symbolic_executor import SymbolicExecutor, execute_symbolically
from defect_identifier.identifier import Identifier
from defect_identifier.registry import DefectRegistry
from reporting.reporter import AnalysisReporter
import global_params

log = logging.getLogger(__name__)


class NFTDefectsAnalyzer:
    """Modern facade for NFT defect analysis with clean API."""
    
    def __init__(self):
        self.defect_registry = DefectRegistry()
        self.reporter = AnalysisReporter()
        self.analysis_results: Dict[str, Any] = {}
        
    def analyze_contract(self, 
                        disasm_file: str, 
                        source_map: Optional[Any] = None,
                        slot_map: Optional[Any] = None) -> Tuple[Dict[str, Any], int]:
        """
        Analyze a contract for NFT defects.
        
        Args:
            disasm_file: Path to disassembly file
            source_map: Source mapping information
            slot_map: Storage slot mapping
            
        Returns:
            Tuple of (results dictionary, exit_code)
        """
        start_time = time.time()
        
        try:
            # Execute symbolic analysis
            sym_exec_result = execute_symbolically(disasm_file, source_map, slot_map)
            
            # Build results structure
            results = self._build_analysis_results(sym_exec_result, start_time)
            
            # Detect defects using registry
            detection_results = self.defect_registry.detect_all(
                source_map, sym_exec_result.problematic_pcs
            )
            
            # Update results with defect information
            self._update_results_with_defects(results, detection_results, source_map)
            
            # Generate and display report
            self._generate_report(results, start_time, sym_exec_result)
            
            # Determine exit code
            exit_code = 1 if self.defect_registry.has_any_defects() else 0
            
            return results, exit_code
            
        except Exception as e:
            log.error(f"Analysis failed: {e}")
            return self._create_error_result(start_time, str(e)), 1
    
    def _build_analysis_results(self, sym_exec_result: Any, start_time: float) -> Dict[str, Any]:
        """Build the analysis results structure."""
        results = {
            'analysis': {},
            'bool_defect': {},
            'evm_code_coverage': len(sym_exec_result.visited_pcs),
            'instructions': len(sym_exec_result.visited_pcs),  # Simplified
            'time': time.time() - start_time,
            'address': global_params.CONTRACT_ADDRESS,
            'contract_count': global_params.CONTRACT_COUNT,
            'storage_var_count': global_params.STORAGE_VAR_COUNT,
            'pub_fun_count': global_params.PUB_FUN_COUNT,
            'visited_pcs': list(sym_exec_result.visited_pcs),
            'problematic_pcs': sym_exec_result.problematic_pcs
        }
        return results
    
    def _update_results_with_defects(self, results: Dict[str, Any], 
                                   detection_results: Dict[str, Any], 
                                   source_map: Any) -> None:
        """Update results with defect detection information."""
        # Map detector names to result keys
        key_mapping = {
            'ERC721 Standard Violation': 'violation',
            'ERC721 Reentrancy': 'reentrancy',
            'Risky Mutable Proxy': 'proxy',
            'Unlimited Minting': 'unlimited_minting',
            'Public Burn': 'burn'
        }
        
        for detector_name, result in detection_results.items():
            key = key_mapping.get(detector_name, detector_name.lower().replace(' ', '_'))
            
            if source_map:
                results['analysis'][key] = result.warnings
            else:
                results['analysis'][key] = result.is_defective
                
            results['bool_defect'][key] = result.is_defective
    
    def _generate_report(self, results: Dict[str, Any], start_time: float, 
                        sym_exec_result: Any) -> None:
        """Generate and display analysis report."""
        analysis_stats = {
            'execution_time': time.time() - start_time,
            'evm_code_coverage': results.get('evm_code_coverage', 0),
            'instructions': results.get('instructions', 0)
        }
        
        self.reporter.print_final_report(self.defect_registry, analysis_stats)
        self.reporter.log_defect_summary(self.defect_registry)
    
    def _create_error_result(self, start_time: float, error_message: str) -> Dict[str, Any]:
        """Create error result when analysis fails."""
        return {
            'analysis': {'error': error_message},
            'bool_defect': {},
            'time': time.time() - start_time,
            'error': error_message
        }
    
    def analyze_solidity_file(self, solidity_file: str, contract_names: list) -> Tuple[Dict[str, Any], int]:
        """
        Analyze a Solidity file (high-level convenience method).
        
        Args:
            solidity_file: Path to Solidity file
            contract_names: List of contract names to analyze
            
        Returns:
            Tuple of (results dictionary, exit_code)
        """
        # This would integrate with the existing compilation pipeline
        # For now, use the legacy approach but with modern backend
        return Identifier.detect_defects(
            instructions={},  # Would be populated by compilation
            results={},
            g_src_map=None,  # Would be populated by compilation  
            visited_pcs=set(),
            global_problematic_pcs={},
            begin=time.time(),
            g_disasm_file=solidity_file.replace('.sol', '.evm.disasm')
        )


def analyze_contract_modern(disasm_file: str, source_map: Optional[Any] = None,
                           slot_map: Optional[Any] = None) -> Tuple[Dict[str, Any], int]:
    """
    Modern analysis function with clean API.
    
    This is the recommended entry point for new code.
    """
    analyzer = NFTDefectsAnalyzer()
    return analyzer.analyze_contract(disasm_file, source_map, slot_map)


def analyze_solidity_modern(solidity_file: str, contract_names: list) -> Tuple[Dict[str, Any], int]:
    """
    Modern analysis of Solidity file with clean API.
    
    This would handle compilation and then analysis.
    """
    analyzer = NFTDefectsAnalyzer()
    return analyzer.analyze_solidity_file(solidity_file, contract_names)