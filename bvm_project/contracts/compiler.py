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
        
        # First pass: collect variables
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                if isinstance(node.targets[0], ast.Name):
                    var_name = node.targets[0].id
                    if isinstance(node.value, ast.Num):
                        variables[var_name] = node.value.n
        
        # Second pass: process operations
        for node in tree.body:
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.BinOp):
                # Get left and right values
                left = node.value.left.id
                right = node.value.right.id
                
                # Push values to stack
                bytecode.extend([
                    Opcode.PUSH1, variables[left],
                    Opcode.PUSH1, variables[right]
                ])
                
                # Add operation
                if isinstance(node.value.op, ast.Add):
                    bytecode.append(Opcode.ADD)
                elif isinstance(node.value.op, ast.Sub):
                    bytecode.append(Opcode.SUB)
                elif isinstance(node.value.op, ast.Mult):
                    bytecode.append(Opcode.MUL)
                elif isinstance(node.value.op, ast.Div):
                    bytecode.append(Opcode.DIV)
                
                # Store result (using variable name hash as storage key)
                storage_key = hash(node.targets[0].id) % 256
                storage_map[node.targets[0].id] = storage_key
                bytecode.extend([
                    Opcode.PUSH1, storage_key,
                    Opcode.SSTORE
                ])
        
        # Add STOP opcode
        bytecode.append(Opcode.STOP)
        
        return bytes(bytecode), storage_map
