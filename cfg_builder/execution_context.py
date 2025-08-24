"""Execution context and state management for symbolic execution."""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Any, Optional
import z3


@dataclass
class ExecutionState:
    """Encapsulates the execution state for symbolic execution."""
    
    # Core execution state
    stack: List[Any] = field(default_factory=list)
    memory: List[Any] = field(default_factory=list)
    visited_pcs: Set[int] = field(default_factory=set)
    visited_edges: Set[str] = field(default_factory=set)
    
    # Analysis state
    global_state: Dict[str, Any] = field(default_factory=dict)
    path_conditions: List[Any] = field(default_factory=list)
    sha3_list: Dict[str, Any] = field(default_factory=dict)
    analysis: Dict[str, Any] = field(default_factory=dict)
    
    # Defect tracking
    problematic_pcs: Dict[str, List[int]] = field(default_factory=dict)
    
    # Execution metrics
    depth: int = 0
    gas_used: int = 0
    loop_count: int = 0
    
    def __post_init__(self):
        """Initialize default problematic PC categories."""
        self.problematic_pcs = {
            'violation_defect': [],
            'reentrancy_defect': [], 
            'proxy_defect': [],
            'unlimited_minting_defect': [],
            'burn_defect': []
        }
    
    def add_problematic_pc(self, defect_type: str, pc: int) -> None:
        """Add a problematic program counter to the specified defect category."""
        if defect_type in self.problematic_pcs:
            if pc not in self.problematic_pcs[defect_type]:
                self.problematic_pcs[defect_type].append(pc)
    
    def has_visited_pc(self, pc: int) -> bool:
        """Check if a program counter has been visited."""
        return pc in self.visited_pcs
    
    def add_visited_pc(self, pc: int) -> None:
        """Mark a program counter as visited."""
        self.visited_pcs.add(pc)
    
    def add_visited_edge(self, edge: str) -> None:
        """Mark an edge as visited."""
        self.visited_edges.add(edge)
    
    def has_visited_edge(self, edge: str) -> bool:
        """Check if an edge has been visited."""
        return edge in self.visited_edges
    
    def update_global_state(self, key: str, value: Any) -> None:
        """Update the global state with a key-value pair."""
        self.global_state[key] = value
    
    def add_path_condition(self, condition: Any) -> None:
        """Add a path condition to the current execution path."""
        self.path_conditions.append(condition)
    
    def increment_depth(self) -> None:
        """Increment the execution depth."""
        self.depth += 1
    
    def decrement_depth(self) -> None:
        """Decrement the execution depth."""
        self.depth -= 1
    
    def increment_loop_count(self) -> None:
        """Increment the loop counter."""
        self.loop_count += 1
    
    def reset_loop_count(self) -> None:
        """Reset the loop counter."""
        self.loop_count = 0
    
    def add_gas_used(self, gas: int) -> None:
        """Add gas used to the total."""
        self.gas_used += gas
    
    def is_exceeding_limits(self) -> bool:
        """Check if execution is exceeding any limits."""
        return (self.depth > global_params.DEPTH_LIMIT or 
                self.gas_used > global_params.GAS_LIMIT or
                self.loop_count > global_params.LOOP_LIMIT)


@dataclass  
class ExecutionContext:
    """Context for managing multiple execution states and shared resources."""
    
    # Shared resources
    solver: z3.Solver = field(default_factory=z3.Solver)
    source_map: Optional[Any] = None
    slot_map: Optional[Any] = None
    disasm_file: Optional[str] = None
    
    # Execution states
    active_states: List[ExecutionState] = field(default_factory=list)
    completed_states: List[ExecutionState] = field(default_factory=list)
    
    # Analysis results
    results: Dict[str, Any] = field(default_factory=dict)
    
    def initialize_solver(self, timeout: int = 1000) -> None:
        """Initialize the Z3 solver with timeout."""
        self.solver = z3.Solver()
        self.solver.set("timeout", timeout)
    
    def add_active_state(self, state: ExecutionState) -> None:
        """Add an active execution state."""
        self.active_states.append(state)
    
    def move_to_completed(self, state: ExecutionState) -> None:
        """Move a state from active to completed."""
        if state in self.active_states:
            self.active_states.remove(state)
            self.completed_states.append(state)
    
    def has_active_states(self) -> bool:
        """Check if there are any active execution states."""
        return len(self.active_states) > 0
    
    def get_next_active_state(self) -> Optional[ExecutionState]:
        """Get the next active execution state (FIFO)."""
        return self.active_states.pop(0) if self.active_states else None
    
    def merge_results(self) -> Dict[str, Any]:
        """Merge results from all completed states."""
        merged = {
            'analysis': {},
            'bool_defect': {},
            'problematic_pcs': {},
            'visited_pcs': set(),
            'visited_edges': set(),
            'gas_used': 0,
            'max_depth': 0
        }
        
        for state in self.completed_states:
            # Merge problematic PCs
            for defect_type, pcs in state.problematic_pcs.items():
                if defect_type not in merged['problematic_pcs']:
                    merged['problematic_pcs'][defect_type] = []
                merged['problematic_pcs'][defect_type].extend(pcs)
            
            # Merge visited PCs and edges
            merged['visited_pcs'].update(state.visited_pcs)
            merged['visited_edges'].update(state.visited_edges)
            
            # Track maximums
            merged['gas_used'] = max(merged['gas_used'], state.gas_used)
            merged['max_depth'] = max(merged['max_depth'], state.depth)
        
        return merged