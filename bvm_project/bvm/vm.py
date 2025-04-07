from .opcodes import Opcode, OPCODE_NAMES
from .exceptions import *

class BVM:
    MAX_STACK_DEPTH = 1024
    WORD_SIZE = 32  # bytes
    
    def __init__(self, world_state):
        self.world_state = world_state
        self.reset()
    
    def reset(self):
        self.pc = 0  # Program counter
        self.stack = []
        self.memory = bytearray()
        self.gas_remaining = 1_000_000  # Start with fixed gas for simplicity
        self.return_data = bytearray()
        self.stopped = False
        self.code = bytearray()
        self.storage = {}
    
    def execute(self, code):
        """Execute bytecode in the VM"""
        self.reset()
        self.code = code
        
        while not self.stopped and self.pc < len(self.code):
            opcode = self.code[self.pc]
            self.pc += 1
            
            try:
                self.execute_opcode(opcode)
            except VMException as e:
                self.stopped = True
                print(f"VM Error: {str(e)}")
                return {
                    'success': False,
                    'error': str(e),
                    'stack': self.stack
                }
        
        return {
            'success': True,
            'stack': self.stack,
            'storage': self.storage
        }
    
    def execute_opcode(self, opcode):
        """Execute a single opcode"""
        if opcode == Opcode.ADD:
            a = self.stack_pop()
            b = self.stack_pop()
            self.stack_push(a + b)
        
        elif opcode == Opcode.SUB:
            a = self.stack_pop()
            b = self.stack_pop()
            self.stack_push(b - a)
        
        elif opcode == Opcode.MUL:
            a = self.stack_pop()
            b = self.stack_pop()
            self.stack_push(a * b)
        
        elif opcode == Opcode.DIV:
            a = self.stack_pop()
            b = self.stack_pop()
            self.stack_push(0 if b == 0 else b // a)
        
        elif opcode == Opcode.PUSH1:
            if self.pc >= len(self.code):
                raise InvalidOpcodeError("PUSH1 without byte")
            value = self.code[self.pc]
            self.pc += 1
            self.stack_push(value)
        
        elif opcode == Opcode.POP:
            self.stack_pop()
        
        elif opcode == Opcode.SSTORE:
            key = self.stack_pop()
            value = self.stack_pop()
            self.storage[key] = value
        
        elif opcode == Opcode.SLOAD:
            key = self.stack_pop()
            value = self.storage.get(key, 0)
            self.stack_push(value)
        
        elif opcode == Opcode.STOP:
            self.stopped = True
        
        else:
            raise InvalidOpcodeError(f"Unknown opcode: {hex(opcode)}")
    
    def stack_push(self, value):
        if len(self.stack) >= self.MAX_STACK_DEPTH:
            raise StackOverflowError()
        self.stack.append(value)
    
    def stack_pop(self):
        if not self.stack:
            raise StackUnderflowError()
        return self.stack.pop()
