from bvm_project.compiler.python_compiler import PythonToBVMCompiler
from bvm_project.vm.bvm import BVM

contract = """
a = 3
b = 5
result = a + b
storage[0] = result
"""

compiler = PythonToBVMCompiler()
bytecode = compiler.compile(contract)

vm = BVM(bytecode)
vm.run()

print("Final Storage State:", vm.storage.storage)
print("Remaining Gas:", vm.gas)

