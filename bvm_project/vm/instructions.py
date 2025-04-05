# bvm_project/vm/instructions.py

from .opcodes import OPCODES, GAS_COST

class BaseInstruction:
    def __init__(self, vm):
        self.vm = vm

    def execute(self):
        raise NotImplementedError

class Stop(BaseInstruction):
    def execute(self):
        self.vm.running = False

class Add(BaseInstruction):
    def execute(self):
        self.vm.gas -= GAS_COST['ADD']
        a = self.vm.stack.pop()
        b = self.vm.stack.pop()
        self.vm.stack.push(a + b)

class Push1(BaseInstruction):
    def execute(self):
        self.vm.gas -= GAS_COST['PUSH1']
        value = self.vm.bytecode[self.vm.pc]
        self.vm.pc += 1
        self.vm.stack.push(value)

class SStore(BaseInstruction):
    def execute(self):
        self.vm.gas -= GAS_COST['SSTORE']
        value = self.vm.stack.pop()  # pop value first
        key = self.vm.stack.pop()    # then key
        self.vm.storage.sstore(key, value)


