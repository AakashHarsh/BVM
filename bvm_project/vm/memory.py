# bvm_project/vm/memory.py

class Memory:
    def __init__(self):
        self.memory = {}

    def load(self, address):
        return self.memory.get(address, 0)

    def store(self, address, value):
        self.memory[address] = value
