"""Modern symbolic execution engine with clean architecture."""

import logging
from typing import Dict, List, Set, Any, Optional, Callable
from dataclasses import dataclass
from .execution_context import ExecutionContext, ExecutionState
from .basicblock import BasicBlock
from .opcode_handlers import OpcodeRegistry, ExecutionResult
import global_params

log = logging.getLogger(__name__)


@dataclass
class SymbolicExecutionResult:
    """Results from symbolic execution analysis."""
    
    visited_pcs: Set[int]
    visited_edges: Set[str]
    problematic_pcs: Dict[str, List[int]]
    execution_states: List[ExecutionState]
    gas_used: int
    max_depth: int
    timed_out: bool = False
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary format."""
        return {
            'visited_pcs': list(self.visited_pcs),
            'visited_edges': list(self.visited_edges),
            'problematic_pcs': self.problematic_pcs,
            'gas_used': self.gas_used,
            'max_depth': self.max_depth,
            'timed_out': self.timed_out,
            'error': self.error
        }


class SymbolicExecutor:
    """Main symbolic execution engine with clean architecture."""
    
    def __init__(self, disasm_file: str, source_map: Optional[Any] = None, 
                 slot_map: Optional[Any] = None):
        self.disasm_file = disasm_file
        self.source_map = source_map
        self.slot_map = slot_map
        self.context = ExecutionContext()
        self.context.disasm_file = disasm_file
        self.context.source_map = source_map
        self.context.slot_map = slot_map
        self.context.initialize_solver(global_params.TIMEOUT)
        
        # Control flow graph components
        self.vertices: Dict[int, BasicBlock] = {}
        self.edges: Dict[int, List[int]] = {}
        self.instructions: Dict[int, Any] = {}
        
        # Opcode handling
        self.opcode_registry = OpcodeRegistry()
    
    def execute(self) -> SymbolicExecutionResult:
        """
        Execute symbolic analysis on the contract.
        
        Returns:
            SymbolicExecutionResult containing analysis results
        """
        try:
            self._build_cfg()
            self._initialize_execution()
            return self._run_symbolic_execution()
        except Exception as e:
            log.error(f"Symbolic execution failed: {e}")
            return SymbolicExecutionResult(
                visited_pcs=set(),
                visited_edges=set(),
                problematic_pcs={},
                execution_states=[],
                gas_used=0,
                max_depth=0,
                error=str(e)
            )
    
    def _build_cfg(self) -> None:
        """Build the control flow graph from disassembly."""
        log.info("Building CFG...")
        # TODO: Implement CFG building logic
        # This would replace the existing collect_vertices, construct_bb, etc.
        pass
    
    def _initialize_execution(self) -> None:
        """Initialize the execution with starting state."""
        initial_state = ExecutionState()
        
        # Set up initial global state
        initial_state.global_state = self._get_initial_global_state()
        initial_state.path_conditions = []
        
        self.context.add_active_state(initial_state)
    
    def _get_initial_global_state(self) -> Dict[str, Any]:
        """Create initial global state for execution."""
        return {
            'pc': 0,
            'balance': 0,
            'storage': {},
            'caller': 0,
            'origin': 0,
            'gasprice': 0,
            'coinbase': 0,
            'timestamp': 0,
            'number': 0,
            'difficulty': 0,
            'gaslimit': global_params.GAS_LIMIT,
            'chainid': 1,
            'selfbalance': 0
        }
    
    def _run_symbolic_execution(self) -> SymbolicExecutionResult:
        """
        Main symbolic execution loop.
        
        This method implements the core execution loop that processes all
        active execution states until completion or until limits are reached.
        
        The loop follows a worklist algorithm where states are processed
        in FIFO order, exploring all possible execution paths.
        
        Returns:
            SymbolicExecutionResult: Aggregated results from all completed states
        """
        log.info("Starting symbolic execution...")
        
        while self.context.has_active_states():
            state = self.context.get_next_active_state()
            
            if state.is_exceeding_limits():
                log.debug("Execution state exceeded limits, skipping")
                continue
            
            try:
                self._execute_state(state)
            except Exception as e:
                log.warning(f"Execution state failed: {e}")
                # Even if state fails, we might have partial results
                self.context.move_to_completed(state)
        
        return self._collect_results()
    
    def _execute_state(self, state: ExecutionState) -> None:
        """Execute a single execution state."""
        current_pc = state.global_state['pc']
        
        if state.has_visited_pc(current_pc):
            log.debug(f"PC {current_pc} already visited, skipping")
            self.context.move_to_completed(state)
            return
        
        state.add_visited_pc(current_pc)
        
        # Get and execute the current instruction
        instruction = self._get_instruction(current_pc)
        if not instruction:
            log.debug(f"No instruction at PC {current_pc}")
            self.context.move_to_completed(state)
            return
        
        try:
            # Execute the instruction and get next states
            next_states = self._execute_instruction(instruction, state)
            
            # Add new states to context
            for next_state in next_states:
                if not next_state.is_exceeding_limits():
                    self.context.add_active_state(next_state)
            
            # Current state is completed
            self.context.move_to_completed(state)
            
        except Exception as e:
            log.error(f"Failed to execute instruction at PC {current_pc}: {e}")
            self.context.move_to_completed(state)
    
    def _get_instruction(self, pc: int) -> Optional[Any]:
        """Get instruction at program counter."""
        return self.instructions.get(pc)
    
    def _execute_instruction(self, instruction: Any, state: ExecutionState) -> List[ExecutionState]:
        """
        Execute a single instruction using the opcode handler system.
        
        This replaces the massive switch statement with a clean, modular approach
        where each opcode has its own handler class.
        """
        # Extract opcode and operands from instruction
        opcode = instruction.get('opcode', '')
        operands = instruction.get('operands', [])
        
        # Execute using opcode registry
        result = self.opcode_registry.execute_opcode(opcode, state, operands)
        
        if result.error:
            log.warning(f"Error executing {opcode}: {result.error}")
            
        # Update PC for all next states (unless they have custom PC set)
        for next_state in result.next_states:
            if 'pc' not in next_state.global_state or next_state.global_state['pc'] == state.global_state['pc']:
                next_state.global_state['pc'] = state.global_state['pc'] + 1
        
        return result.next_states
    
    def _collect_results(self) -> SymbolicExecutionResult:
        """Collect results from all completed execution states."""
        merged = self.context.merge_results()
        
        return SymbolicExecutionResult(
            visited_pcs=merged['visited_pcs'],
            visited_edges=merged['visited_edges'],
            problematic_pcs=merged['problematic_pcs'],
            execution_states=self.context.completed_states,
            gas_used=merged['gas_used'],
            max_depth=merged['max_depth']
        )


def execute_symbolically(disasm_file: str, source_map: Optional[Any] = None, 
                        slot_map: Optional[Any] = None) -> SymbolicExecutionResult:
    """
    High-level function to execute symbolic analysis.
    
    Args:
        disasm_file: Path to disassembly file
        source_map: Source mapping information
        slot_map: Storage slot mapping
        
    Returns:
        SymbolicExecutionResult with analysis results
    """
    executor = SymbolicExecutor(disasm_file, source_map, slot_map)
    return executor.execute()