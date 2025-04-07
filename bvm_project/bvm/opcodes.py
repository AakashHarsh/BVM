class Opcode:
    # Arithmetic operations
    ADD = 0x01
    SUB = 0x02
    MUL = 0x03
    DIV = 0x04
    
    # Stack operations
    PUSH1 = 0x60
    POP = 0x50
    
    # Control flow
    STOP = 0x00
    
    # Storage
    SSTORE = 0x55
    SLOAD = 0x54

OPCODE_NAMES = {
    0x01: 'ADD',
    0x02: 'SUB',
    0x03: 'MUL',
    0x04: 'DIV',
    0x60: 'PUSH1',
    0x50: 'POP',
    0x00: 'STOP',
    0x55: 'SSTORE',
    0x54: 'SLOAD'
}
