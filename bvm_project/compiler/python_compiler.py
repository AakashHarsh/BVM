import ast
from bvm_project.vm.opcodes import OPCODES

class PythonToBVMCompiler(ast.NodeVisitor):
    def __init__(self):
        self.bytecode = []
        self.vars_map = {}
        self.temp_id = 0

    def compile(self, code):
        tree = ast.parse(code)
        self.visit(tree)
        self.bytecode.append(OPCODES['STOP'])
        return self.bytecode

    def visit_Assign(self, node):
        target = node.targets[0]
        value = node.value

        # Handle storage[...] = some_value
        if isinstance(target, ast.Subscript):
            if isinstance(target.value, ast.Name) and target.value.id == 'storage':
                index_node = target.slice
                if isinstance(index_node, ast.Constant):
                    index = index_node.value
                elif isinstance(index_node, ast.Index):  # Python < 3.9
                    index = index_node.value.n
                else:
                    raise Exception("Unsupported storage index type")

                if isinstance(value, ast.Name):
                    val = self._resolve_value(value)
                    self.bytecode.extend([OPCODES['PUSH1'], index])  # KEY
                    self.bytecode.extend([OPCODES['PUSH1'], val])    # VALUE
                    self.bytecode.append(OPCODES['SSTORE'])


                else:
                    resolved_val = self._resolve_value(value)
                    self.bytecode.extend([OPCODES['PUSH1'], resolved_val])  # VALUE
                    self.bytecode.extend([OPCODES['PUSH1'], index])         # KEY
                    self.bytecode.append(OPCODES['SSTORE'])
                return

        # Handle regular variable assignment
        if isinstance(target, ast.Name):
            var_name = target.id
            if isinstance(value, ast.BinOp) and isinstance(value.op, ast.Add):
                lval = self._resolve_value(value.left)
                rval = self._resolve_value(value.right)
                self.bytecode.extend([OPCODES['PUSH1'], lval])
                self.bytecode.extend([OPCODES['PUSH1'], rval])
                self.bytecode.append(OPCODES['ADD'])
                result = lval + rval  # evaluate the result statically
                self.vars_map[var_name] = result  # store actual value

            else:
                val = self._resolve_value(value)
                self.bytecode.extend([OPCODES['PUSH1'], val])
                self.vars_map[var_name] = val


    def visit_Expr(self, node):
        pass

    def _resolve_value(self, node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            if node.id not in self.vars_map:
                raise Exception(f"Variable '{node.id}' not defined")
            val = self.vars_map[node.id]
            if val == 'STACK_TOP':
                raise Exception(f"Variable '{node.id}' is only on stack and cannot be reused directly")
            return val
        else:
            raise Exception(f"Unsupported value type: {type(node)}")

