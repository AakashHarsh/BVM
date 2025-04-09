from bvm.opcodes import Opcode
import ast

class Compiler:
    @staticmethod
    def compile(contract_source):
        """Compile Python script to BVM bytecode"""
        bytecode = bytearray()
        variables = {}
        storage_map = {}
        
        # Parse the AST
        tree = ast.parse(contract_source)
        
        # First pass: collect variables and constants
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                if isinstance(node.targets[0], ast.Name):
                    var_name = node.targets[0].id
                    if isinstance(node.value, ast.Num):
                        variables[var_name] = node.value.n
                    elif isinstance(node.value, ast.Name) and node.value.id in variables:
                        variables[var_name] = variables[node.value.id]
        
        # Second pass: process operations
        for node in tree.body:
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                target_var = node.targets[0].id
                storage_key = hash(target_var) % 256
                storage_map[target_var] = storage_key

                # Handle the RHS expression
                def compile_expression(expr, bytecode):
                    """Recursively compile expressions"""
                    if isinstance(expr, ast.Num):
                        bytecode.extend([Opcode.PUSH1, expr.n])
                    elif isinstance(expr, ast.Name):
                        bytecode.extend([Opcode.PUSH1, variables[expr.id]])
                    elif isinstance(expr, ast.BinOp):
                        compile_expression(expr.left, bytecode)
                        compile_expression(expr.right, bytecode)
                        if isinstance(expr.op, ast.Add):
                            bytecode.append(Opcode.ADD)
                        elif isinstance(expr.op, ast.Sub):
                            bytecode.append(Opcode.SUB)
                        elif isinstance(expr.op, ast.Mult):
                            bytecode.append(Opcode.MUL)
                        elif isinstance(expr.op, ast.Div):
                            bytecode.append(Opcode.DIV)
                        elif isinstance(expr.op, ast.Mod):
                            bytecode.append(Opcode.MOD)
                    elif isinstance(expr, ast.Compare):
                        compile_expression(expr.left, bytecode)
                        compile_expression(expr.comparators[0], bytecode)
                        if isinstance(expr.ops[0], ast.Lt):
                            bytecode.append(Opcode.LT)
                        elif isinstance(expr.ops[0], ast.Gt):
                            bytecode.append(Opcode.GT)
                        elif isinstance(expr.ops[0], ast.Eq):
                            bytecode.append(Opcode.EQ)
                    else:
                        raise ValueError(f"Unsupported expression type: {type(expr)}")

                # Compile the right-hand side
                compile_expression(node.value, bytecode)
                
                # Store the result
                bytecode.extend([
                    Opcode.PUSH1, storage_key,
                    Opcode.SSTORE
                ])
        
        bytecode.append(Opcode.STOP)
        return bytes(bytecode), storage_map
