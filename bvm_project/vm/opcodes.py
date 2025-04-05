# bvm_project/vm/opcodes.py

OPCODES = {
    'STOP': 0x00,
    'ADD': 0x01,
    'PUSH1': 0x60,
    'SSTORE': 0x55,
}

GAS_COST = {
    'STOP': 0,
    'ADD': 3,
    'PUSH1': 3,
    'SSTORE': 200,
}

