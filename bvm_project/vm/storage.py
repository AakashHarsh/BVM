# bvm_project/vm/storage.py

class Storage:
    def __init__(self):
        self.storage = {}

    def sstore(self, key, value):
        self.storage[key] = value
