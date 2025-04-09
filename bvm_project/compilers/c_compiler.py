from pycparser import c_parser, c_ast
from bvm.opcodes import Opcode

class CCompiler:
    @staticmethod
    def compile(source: str) -> bytes:
        parser = c_parser.CParser()
        ast = parser.parse(source)
        bytecode = bytearray()
        variables = {}
        storage_map = {}
        next_storage = 0
        
        def handle_expression(expr):
            if isinstance(expr, c_ast.Constant):
                bytecode.extend([Opcode.PUSH1, int(expr.value)])
            elif isinstance(expr, c_ast.ID):
                bytecode.extend([Opcode.PUSH1, storage_map[expr.name], Opcode.SLOAD])
            elif isinstance(expr, c_ast.BinaryOp):
                handle_expression(expr.left)
                handle_expression(expr.right)
                if expr.op == '+': bytecode.append(Opcode.ADD)
                elif expr.op == '-': bytecode.append(Opcode.SUB)
                elif expr.op == '*': bytecode.append(Opcode.MUL)
                elif expr.op == '/': bytecode.append(Opcode.DIV)
                elif expr.op == '>': bytecode.append(Opcode.GT)
                elif expr.op == '<': bytecode.append(Opcode.LT)
                elif expr.op == '==': bytecode.append(Opcode.EQ)
                print("mai bahar wale ke bahar wale ke andar hoon")
            else: #isinstance(expr, c_ast.Compare):
                handle_expression(expr.left)   # Push left operand (a)
                handle_expression(expr.right)  # Push right operand (2)
                print("mai bahar wale ke andar hoon")
                if isinstance(expr.ops[0], c_ast.Gt):
                    print("mai andar hoon")
                    bytecode.append(Opcode.GT)
                    bytecode.append(Opcode.POP)

        for node in ast.ext:
            if isinstance(node, c_ast.FuncDef) and node.decl.name == 'main':
                for item in node.body.block_items:
                    if isinstance(item, c_ast.Decl) and item.init:
                        var_name = item.name
                        storage_key = hash(var_name) % 256  # MATCH PYTHON'S HASHING
                        storage_map[var_name] = storage_key
                        handle_expression(item.init)
                        bytecode.extend([Opcode.PUSH1, storage_key, Opcode.SSTORE])
        
        bytecode.append(Opcode.STOP)
        return bytes(bytecode), storage_map 
