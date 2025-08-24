"""Modular opcode handling system for symbolic execution."""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from .execution_context import ExecutionState
import z3


@dataclass
class ExecutionResult:
    """Result of executing an opcode."""
    
    next_states: List[ExecutionState]
    gas_used: int = 0
    should_continue: bool = True
    error: Optional[str] = None


class OpcodeHandler:
    """Base class for opcode handlers."""
    
    def __init__(self, opcode_name: str, gas_cost: int = 0):
        self.opcode_name = opcode_name
        self.gas_cost = gas_cost
    
    def execute(self, state: ExecutionState, operands: List[Any]) -> ExecutionResult:
        """
        Execute the opcode.
        
        Args:
            state: Current execution state
            operands: List of operands for the instruction
            
        Returns:
            ExecutionResult with next states and metadata
        """
        raise NotImplementedError("Subclasses must implement execute()")
    
    def _consume_gas(self, state: ExecutionState) -> None:
        """Consume gas for this operation."""
        state.add_gas_used(self.gas_cost)


class StackOpcodeHandler(OpcodeHandler):
    """Handler for stack manipulation opcodes."""
    
    def __init__(self, opcode_name: str, gas_cost: int = 3):
        super().__init__(opcode_name, gas_cost)
    
    def execute(self, state: ExecutionState, operands: List[Any]) -> ExecutionResult:
        self._consume_gas(state)
        
        if self.opcode_name == "PUSH1":
            return self._handle_push(state, operands, 1)
        elif self.opcode_name == "PUSH2":
            return self._handle_push(state, operands, 2)
        # Add more PUSH handlers...
        
        elif self.opcode_name == "POP":
            return self._handle_pop(state)
        
        return ExecutionResult(next_states=[state])
    
    def _handle_push(self, state: ExecutionState, operands: List[Any], size: int) -> ExecutionResult:
        if operands:
            value = operands[0]
            state.stack.append(value)
        return ExecutionResult(next_states=[state])
    
    def _handle_pop(self, state: ExecutionState) -> ExecutionResult:
        if state.stack:
            state.stack.pop()
        return ExecutionResult(next_states=[state])


class ArithmeticOpcodeHandler(OpcodeHandler):
    """Handler for arithmetic opcodes."""
    
    def __init__(self, opcode_name: str, gas_cost: int = 3):
        super().__init__(opcode_name, gas_cost)
    
    def execute(self, state: ExecutionState, operands: List[Any]) -> ExecutionResult:
        self._consume_gas(state)
        
        if len(state.stack) < 2:
            return ExecutionResult(next_states=[state], error="Stack underflow")
        
        a = state.stack.pop()
        b = state.stack.pop()
        
        if self.opcode_name == "ADD":
            result = a + b
        elif self.opcode_name == "SUB":
            result = a - b
        elif self.opcode_name == "MUL":
            result = a * b
        elif self.opcode_name == "DIV":
            result = z3.simplify(a / b) if isinstance(b, z3.Expr) and b != 0 else 0
        else:
            return ExecutionResult(next_states=[state], error=f"Unknown arithmetic opcode: {self.opcode_name}")
        
        state.stack.append(result)
        return ExecutionResult(next_states=[state])


class ControlFlowOpcodeHandler(OpcodeHandler):
    """Handler for control flow opcodes."""
    
    def __init__(self, opcode_name: str, gas_cost: int = 8):
        super().__init__(opcode_name, gas_cost)
    
    def execute(self, state: ExecutionState, operands: List[Any]) -> ExecutionResult:
        self._consume_gas(state)
        
        if self.opcode_name == "JUMP":
            return self._handle_jump(state, operands)
        elif self.opcode_name == "JUMPI":
            return self._handle_jumpi(state, operands)
        
        return ExecutionResult(next_states=[state])
    
    def _handle_jump(self, state: ExecutionState, operands: List[Any]) -> ExecutionResult:
        if not state.stack:
            return ExecutionResult(next_states=[state], error="Stack underflow for JUMP")
        
        jump_target = state.stack.pop()
        # Create new state with updated PC
        new_state = self._copy_state(state)
        new_state.global_state['pc'] = jump_target
        
        return ExecutionResult(next_states=[new_state])
    
    def _handle_jumpi(self, state: ExecutionState, operands: List[Any]) -> ExecutionResult:
        if len(state.stack) < 2:
            return ExecutionResult(next_states=[state], error="Stack underflow for JUMPI")
        
        jump_target = state.stack.pop()
        condition = state.stack.pop()
        
        # Create two states: one for taken branch, one for not taken
        taken_state = self._copy_state(state)
        taken_state.global_state['pc'] = jump_target
        taken_state.add_path_condition(condition)
        
        not_taken_state = self._copy_state(state)
        not_taken_state.global_state['pc'] += 1  # Next instruction
        not_taken_state.add_path_condition(z3.Not(condition))
        
        return ExecutionResult(next_states=[taken_state, not_taken_state])
    
    def _copy_state(self, state: ExecutionState) -> ExecutionState:
        """Create a copy of the execution state."""
        return ExecutionState(
            stack=state.stack.copy(),
            memory=state.memory.copy(),
            visited_pcs=state.visited_pcs.copy(),
            visited_edges=state.visited_edges.copy(),
            global_state=state.global_state.copy(),
            path_conditions=state.path_conditions.copy(),
            sha3_list=state.sha3_list.copy(),
            analysis=state.analysis.copy(),
            problematic_pcs=state.problematic_pcs.copy(),
            depth=state.depth,
            gas_used=state.gas_used,
            loop_count=state.loop_count
        )


class StorageOpcodeHandler(OpcodeHandler):
    """Handler for storage opcodes."""
    
    def __init__(self, opcode_name: str, gas_cost: int = 50):
        super().__init__(opcode_name, gas_cost)
    
    def execute(self, state: ExecutionState, operands: List[Any]) -> ExecutionResult:
        self._consume_gas(state)
        
        if self.opcode_name == "SLOAD":
            return self._handle_sload(state)
        elif self.opcode_name == "SSTORE":
            return self._handle_sstore(state)
        
        return ExecutionResult(next_states=[state])
    
    def _handle_sload(self, state: ExecutionState) -> ExecutionResult:
        if not state.stack:
            return ExecutionResult(next_states=[state], error="Stack underflow for SLOAD")
        
        storage_key = state.stack.pop()
        value = state.global_state['storage'].get(storage_key, 0)
        state.stack.append(value)
        
        return ExecutionResult(next_states=[state])
    
    def _handle_sstore(self, state: ExecutionState) -> ExecutionResult:
        if len(state.stack) < 2:
            return ExecutionResult(next_states=[state], error="Stack underflow for SSTORE")
        
        storage_key = state.stack.pop()
        value = state.stack.pop()
        state.global_state['storage'][storage_key] = value
        
        return ExecutionResult(next_states=[state])


class OpcodeRegistry:
    """Registry for opcode handlers."""
    
    def __init__(self):
        self.handlers: Dict[str, OpcodeHandler] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self) -> None:
        """Register default opcode handlers."""
        # Stack operations
        self.register_handler("PUSH1", StackOpcodeHandler("PUSH1", 3))
        self.register_handler("PUSH2", StackOpcodeHandler("PUSH2", 3))
        self.register_handler("POP", StackOpcodeHandler("POP", 2))
        
        # Arithmetic operations
        self.register_handler("ADD", ArithmeticOpcodeHandler("ADD", 3))
        self.register_handler("SUB", ArithmeticOpcodeHandler("SUB", 3))
        self.register_handler("MUL", ArithmeticOpcodeHandler("MUL", 5))
        self.register_handler("DIV", ArithmeticOpcodeHandler("DIV", 5))
        
        # Control flow
        self.register_handler("JUMP", ControlFlowOpcodeHandler("JUMP", 8))
        self.register_handler("JUMPI", ControlFlowOpcodeHandler("JUMPI", 10))
        
        # Storage operations
        self.register_handler("SLOAD", StorageOpcodeHandler("SLOAD", 50))
        self.register_handler("SSTORE", StorageOpcodeHandler("SSTORE", 20000))
    
    def register_handler(self, opcode: str, handler: OpcodeHandler) -> None:
        """Register a handler for an opcode."""
        self.handlers[opcode] = handler
    
    def get_handler(self, opcode: str) -> Optional[OpcodeHandler]:
        """Get handler for an opcode."""
        return self.handlers.get(opcode)
    
    def execute_opcode(self, opcode: str, state: ExecutionState, operands: List[Any]) -> ExecutionResult:
        """Execute an opcode using its registered handler."""
        handler = self.get_handler(opcode)
        if not handler:
            return ExecutionResult(
                next_states=[state], 
                error=f"No handler registered for opcode: {opcode}"
            )
        
        return handler.execute(state, operands)