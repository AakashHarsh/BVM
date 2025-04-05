# bvm_project/vm/stack.py

class Stack:
    def __init__(self):
        self.stack = []

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        if not self.stack:
            raise Exception("Stack underflow")
        return self.stack.pop()

