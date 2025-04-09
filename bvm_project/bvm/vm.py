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
        self.jumpdests = set()
    
    def _preprocess_jumpdests(self):
        """Scan bytecode for JUMPDEST opcodes"""
        for pc, opcode in enumerate(self.code):
            if opcode == Opcode.JUMPDEST:
                self.jumpdests.add(pc)
    
    def execute(self, code):
        """Execute bytecode in the VM"""
        self.reset()
        self.code = code
        self._preprocess_jumpdests()
        
        try:
            while not self.stopped and self.pc < len(self.code):
                opcode = self.code[self.pc]
                print(f"Executing {OPCODE_NAMES.get(opcode, hex(opcode))} at pc={self.pc}")  
                self.pc += 1
                self.execute_opcode(opcode)
            
            return {
                'success': True,
                'stack': self.stack,
                'storage': self.storage,
                'gas_remaining': self.gas_remaining
            }
        except VMException as e:
            print(f"VM Exception at pc={self.pc}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'stack': self.stack,
                'storage': self.storage,
                'pc': self.pc,
                'opcode': OPCODE_NAMES.get(opcode, hex(opcode))
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
    
        elif opcode == Opcode.MOD:
            a = self.stack_pop()
            b = self.stack_pop()
            self.stack_push(0 if b == 0 else b % a)
        
        elif opcode == Opcode.LT:
            a = self.stack_pop()
            b = self.stack_pop()
            self.stack_push(1 if b < a else 0)
        
        elif opcode == Opcode.GT:
            a = self.stack_pop()
            b = self.stack_pop()
            self.stack_push(1 if b > a else 0)
        
        elif opcode == Opcode.EQ:
            a = self.stack_pop()
            b = self.stack_pop()
            self.stack_push(1 if a == b else 0)
        
        elif opcode == Opcode.ISZERO:
            a = self.stack_pop()
            self.stack_push(1 if a == 0 else 0)
        
        elif opcode == Opcode.JUMP:
            dest = self.stack_pop()
            if dest not in self.jumpdests:
                raise InvalidJumpError(f"Invalid JUMP destination: {dest}")
            self.pc = dest
        
        elif opcode == Opcode.JUMPI:
            dest = self.stack_pop()
            condition = self.stack_pop()
            print(f"JUMPI condition: {condition}, dest: {dest}")  # Debug
            if condition != 0:
                if dest not in self.jumpdests:
                    raise InvalidJumpError(f"Invalid JUMPI destination: {dest}")
                self.pc = dest
        
        elif opcode == Opcode.JUMPDEST:
            pass
        
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
