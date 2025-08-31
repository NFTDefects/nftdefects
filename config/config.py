"""Configuration management system for NFTDefects."""

from dataclasses import dataclass, field
from typing import Optional, List
import os


@dataclass
class AnalysisConfig:
    """Configuration for analysis parameters."""
    
    # Timeouts
    timeout: int = 1000  # Z3 timeout in ms
    global_timeout: int = 600  # Symbolic execution timeout in seconds
    
    # Execution limits
    depth_limit: int = 500
    gas_limit: int = 400000000
    loop_limit: int = 200
    
    # Mode flags
    debug_mode: bool = False
    report_mode: bool = False
    print_mode: bool = False
    print_paths: bool = False
    store_result: bool = True
    generate_test_cases: bool = False
    parallel: bool = False
    
    # Solidity compilation
    solc_switch: bool = False
    solc_version: Optional[str] = None
    
    # Analysis targets
    target_contracts: Optional[List[str]] = None
    target_function: Optional[str] = None
    
    # Paths and files
    source: Optional[str] = None
    crawl_dir: str = "./test/"
    
    # Contract metadata
    contract_address: str = ""
    contract_count: int = 0
    storage_var_count: int = 0
    pub_fun_count: int = 0
    
    # NFT-specific constants
    onerc721received_selector: int = 353073666
    onerc721received_selector_shl: Optional[int] = None
    
    @classmethod
    def from_args(cls, args) -> 'AnalysisConfig':
        """Create configuration from command line arguments."""
        config = cls()
        
        # Update from args if provided
        if hasattr(args, 'timeout') and args.timeout:
            config.timeout = args.timeout
        if hasattr(args, 'global_timeout') and args.global_timeout:
            config.global_timeout = args.global_timeout
        if hasattr(args, 'depth_limit') and args.depth_limit:
            config.depth_limit = args.depth_limit
        if hasattr(args, 'gas_limit') and args.gas_limit:
            config.gas_limit = args.gas_limit
        if hasattr(args, 'loop_limit') and args.loop_limit:
            config.loop_limit = args.loop_limit
            
        if hasattr(args, 'debug') and args.debug:
            config.debug_mode = args.debug
        if hasattr(args, 'report') and args.report:
            config.report_mode = args.report
        if hasattr(args, 'paths') and args.paths:
            config.print_paths = args.paths
        if hasattr(args, 'json') and args.json:
            config.store_result = args.json
        if hasattr(args, 'generate_test_cases') and args.generate_test_cases:
            config.generate_test_cases = args.generate_test_cases
        if hasattr(args, 'parallel') and args.parallel:
            config.parallel = args.parallel
        if hasattr(args, 'automated_solc_version_switch') and args.automated_solc_version_switch:
            config.solc_switch = args.automated_solc_version_switch
            
        if hasattr(args, 'solc_version') and args.solc_version:
            config.solc_version = args.solc_version
        if hasattr(args, 'target_contracts') and args.target_contracts:
            config.target_contracts = args.target_contracts
        if hasattr(args, 'target_fselector') and args.target_fselector:
            config.target_function = args.target_fselector
        if hasattr(args, 'source') and args.source:
            config.source = args.source
        if hasattr(args, 'address') and args.address:
            config.contract_address = args.address
            
        return config
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            'timeout': self.timeout,
            'global_timeout': self.global_timeout,
            'depth_limit': self.depth_limit,
            'gas_limit': self.gas_limit,
            'loop_limit': self.loop_limit,
            'debug_mode': self.debug_mode,
            'report_mode': self.report_mode,
            'print_paths': self.print_paths,
            'store_result': self.store_result,
            'generate_test_cases': self.generate_test_cases,
            'parallel': self.parallel,
            'solc_switch': self.solc_switch,
            'solc_version': self.solc_version,
            'target_contracts': self.target_contracts,
            'target_function': self.target_function,
            'source': self.source,
            'contract_address': self.contract_address
        }


# Global configuration instance
_global_config: Optional[AnalysisConfig] = None


def get_config() -> AnalysisConfig:
    """Get the global configuration instance."""
    global _global_config
    if _global_config is None:
        _global_config = AnalysisConfig()
    return _global_config


def set_config(config: AnalysisConfig) -> None:
    """Set the global configuration instance."""
    global _global_config
    _global_config = config


def reset_config() -> None:
    """Reset the global configuration to defaults."""
    global _global_config
    _global_config = AnalysisConfig()