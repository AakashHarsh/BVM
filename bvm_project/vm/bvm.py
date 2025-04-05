# bvm_project/vm/bvm.py

from .stack import Stack
from .memory import Memory
from .storage import Storage
from .opcodes import OPCODES
from .instructions import Stop, Add, Push1, SStore

class BVM:
    def __init__(self, bytecode, gas_limit=1000):
        self.stack = Stack()
        self.memory = Memory()
        self.storage = Storage()
        self.pc = 0
        self.bytecode = bytecode
        self.gas = gas_limit
        self.running = True
        self.instruction_set = {
            OPCODES['STOP']: Stop,
            OPCODES['ADD']: Add,
            OPCODES['PUSH1']: Push1,
            OPCODES['SSTORE']: SStore,
        }

    def fetch(self):
        if self.pc >= len(self.bytecode):
            return OPCODES['STOP']
        opcode = self.bytecode[self.pc]
        self.pc += 1
        return opcode

    def execute(self, opcode):
        instruction_cls = self.instruction_set.get(opcode)
        if not instruction_cls:
            raise Exception(f"Unknown opcode {opcode}")
        instruction_cls(self).execute()

    def run(self):
        while self.running and self.gas > 0:
            opcode = self.fetch()
            self.execute(opcode)
