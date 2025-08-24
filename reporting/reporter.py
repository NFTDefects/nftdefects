"""Reporting module for presenting analysis results."""

import logging
from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich import box
from defect_identifier.registry import DefectRegistry

log = logging.getLogger(__name__)


class AnalysisReporter:
    """Handles presentation and reporting of analysis results."""
    
    def __init__(self):
        self.console = Console()
    
    def create_defect_table(self, registry: DefectRegistry) -> Table:
        """
        Create a formatted table showing defect detection results.
        
        Args:
            registry: DefectRegistry containing detection results
            
        Returns:
            Rich Table object for display
        """
        defect_table = Table(box=box.SIMPLE)
        defect_table.add_column("Defect", justify="right", style="bold", no_wrap=True)
        defect_table.add_column("Status", style="green")
        defect_table.add_column("Location", justify="left", style="cyan")
        
        results = registry.get_results()
        for defect_name, result in results.items():
            status_style = "red" if result.is_defective else "green"
            location = ", ".join(result.locations) if result.locations else "N/A"
            
            defect_table.add_row(
                defect_name,
                f"[{status_style}]{result.is_defective}[/{status_style}]",
                location
            )
        
        return defect_table
    
    def create_stats_table(self, analysis_stats: Dict[str, Any]) -> Table:
        """
        Create a table showing analysis statistics.
        
        Args:
            analysis_stats: Dictionary containing analysis statistics
            
        Returns:
            Rich Table object for display
        """
        param_table = Table()
        param_table.add_column("Time", justify="left", style="cyan", no_wrap=True)
        param_table.add_column("Code Coverage", justify="left", style="yellow", no_wrap=True)
        
        execution_time = analysis_stats.get('execution_time', 0)
        coverage = analysis_stats.get('evm_code_coverage', '0.0')
        
        param_table.add_row(str(round(execution_time, 1)), str(coverage))
        
        instruct_table = Table()
        instruct_table.add_column(
            "Total Instructions",
            justify="left", 
            style="cyan",
            no_wrap=True,
            width=20
        )
        instruct_table.add_row(str(analysis_stats.get('instructions', 0)))
        
        state_table = Table.grid(expand=True)
        state_table.add_column(justify="center")
        state_table.add_row(param_table)
        state_table.add_row(instruct_table)
        
        return state_table
    
    def create_live_table(self, 
                         current_opcode: str,
                         block_coverage: float,
                         current_pc: int,
                         percentage: float,
                         registry: DefectRegistry,
                         current_func: str = "") -> Table:
        """
        Create a live table for real-time analysis display.
        
        Args:
            current_opcode: Currently executing opcode
            block_coverage: Current block coverage percentage
            current_pc: Current program counter
            percentage: Overall analysis percentage
            registry: DefectRegistry with current results
            current_func: Current function being analyzed
            
        Returns:
            Rich Table object for live display
        """
        defect_table = self.create_defect_table(registry)
        
        progress_table = Table(box=box.SIMPLE)
        progress_table.add_column("Metric", style="bold")
        progress_table.add_column("Value", style="cyan")
        
        progress_table.add_row("Current Opcode", current_opcode)
        progress_table.add_row("Block Coverage", f"{block_coverage:.1f}%")
        progress_table.add_row("Current PC", str(current_pc))
        progress_table.add_row("Progress", f"{percentage:.1f}%")
        if current_func:
            progress_table.add_row("Function", current_func)
        
        main_table = Table(title="NFTGuard GENESIS v0.0.1")
        main_table.add_column("Defect Detection", justify="center")
        main_table.add_column("Analysis Progress", justify="center")
        main_table.add_row(defect_table, progress_table)
        
        return main_table
    
    def print_final_report(self, 
                          registry: DefectRegistry,
                          analysis_stats: Dict[str, Any]):
        """
        Print the final analysis report.
        
        Args:
            registry: DefectRegistry containing final results
            analysis_stats: Dictionary containing analysis statistics
        """
        defect_table = self.create_defect_table(registry)
        stats_table = self.create_stats_table(analysis_stats)
        
        reporter = Table(title="NFTGuard GENESIS v0.0.1")
        reporter.add_column("Defect Detection", justify="center")
        reporter.add_column("Execution Stats", justify="center") 
        reporter.add_row(defect_table, stats_table)
        
        self.console.print(reporter)
        
        # Log individual defect information
        for result in registry.get_results().values():
            if result.warnings:
                for warning in result.warnings:
                    log.info(warning)
    
    def log_defect_summary(self, registry: DefectRegistry):
        """Log a summary of detected defects."""
        defective_results = registry.get_defective_results()
        
        if defective_results:
            log.info(f"Found {len(defective_results)} defect type(s):")
            for defect_name in defective_results.keys():
                log.info(f"  - {defect_name}")
        else:
            log.info("No defects detected.")