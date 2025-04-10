# bvm/gas.py
from .opcodes import Opcode

OPCODE_GAS = {
    # Arithmetic operations
    Opcode.STOP: 0,
    Opcode.ADD: 3,
    Opcode.SUB: 3,
    Opcode.MUL: 5,
    Opcode.DIV: 5,
    Opcode.MOD: 5,
    
    # Comparison operations
    Opcode.LT: 3,
    Opcode.GT: 3,
    Opcode.EQ: 3,
    Opcode.ISZERO: 3,
    
    # Stack operations
    Opcode.POP: 2,
    Opcode.PUSH1: 3,
    
    # Storage operations
    Opcode.SLOAD: 2,
    Opcode.SSTORE: 5,
    
    # Control flow
    Opcode.JUMP: 8,
    Opcode.JUMPI: 10,
    Opcode.JUMPDEST: 1,
    Opcode.LTE: 4,
    Opcode.GTE: 4,
}

def get_opcode_gas(opcode: int) -> int:
    """Get gas cost for an opcode"""
    return OPCODE_GAS.get(opcode, 0)
