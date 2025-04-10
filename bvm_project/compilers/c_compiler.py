from pycparser import c_parser, c_ast
from bvm.opcodes import Opcode

class CCompiler:
    @staticmethod
    def compile(source: str) -> bytes:
        parser = c_parser.CParser()
        ast = parser.parse(source)
        bytecode = bytearray()
        storage_map = {}
        jump_placeholders = []
        label_positions = {}
        loop_stack = []

        def get_storage_slot(var_name):
            if var_name not in storage_map:
                slot = len(storage_map) % 256
                storage_map[var_name] = slot
                print(f"Allocated slot {slot} for variable '{var_name}'")
            return storage_map[var_name]

        def handle_expression(expr):
            if isinstance(expr, c_ast.Constant):
                bytecode.extend([Opcode.PUSH1, int(expr.value) & 0xff])
            elif isinstance(expr, c_ast.ID):
                slot = get_storage_slot(expr.name)
                bytecode.extend([Opcode.PUSH1, int(slot) & 0xff, Opcode.SLOAD])
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
            elif isinstance(expr, c_ast.UnaryOp):
                if expr.op == '++' and isinstance(expr.expr, c_ast.ID):
                    var_name = expr.expr.name
                    slot = get_storage_slot(var_name)
                    bytecode.extend([
                        Opcode.PUSH1, int(slot) & 0xff,
                        Opcode.SLOAD,
                        Opcode.PUSH1, 1,
                        Opcode.ADD,
                        Opcode.PUSH1, int(slot) & 0xff,
                        Opcode.SSTORE
                    ])
                elif expr.op == '--' and isinstance(expr.expr, c_ast.ID):
                    var_name = expr.expr.name
                    slot = get_storage_slot(var_name)
                    bytecode.extend([
                        Opcode.PUSH1, int(slot) & 0xff,
                        Opcode.SLOAD,
                        Opcode.PUSH1, 1,
                        Opcode.SUB,
                        Opcode.PUSH1, int(slot) & 0xff,
                        Opcode.SSTORE
                    ])

        def handle_if_statement(node):
            else_label = f"else_{len(jump_placeholders)}"
            end_label = f"end_{len(jump_placeholders)+1}"
            handle_expression(node.cond)
            bytecode.append(Opcode.ISZERO)
            bytecode.extend([Opcode.PUSH1, 0])
            jump_placeholders.append((len(bytecode) - 1, else_label))
            bytecode.append(Opcode.JUMPI)

            if node.iftrue:
                if isinstance(node.iftrue, c_ast.Compound):
                    for item in node.iftrue.block_items:
                        handle_statement(item)
                else:
                    handle_statement(node.iftrue)

            bytecode.extend([Opcode.PUSH1, 0])
            jump_placeholders.append((len(bytecode) - 1, end_label))
            bytecode.append(Opcode.JUMP)

            label_positions[else_label] = len(bytecode)
            bytecode.append(Opcode.JUMPDEST)

            if node.iffalse:
                if isinstance(node.iffalse, c_ast.Compound):
                    for item in node.iffalse.block_items:
                        handle_statement(item)
                else:
                    handle_statement(node.iffalse)

            label_positions[end_label] = len(bytecode)
            bytecode.append(Opcode.JUMPDEST)

        def handle_statement(stmt):
            if isinstance(stmt, c_ast.Decl):
                var_name = stmt.name
                slot = get_storage_slot(var_name)
                if stmt.init:
                    handle_expression(stmt.init)
                    bytecode.extend([Opcode.PUSH1, int(slot) & 0xff, Opcode.SSTORE])
            elif isinstance(stmt, c_ast.Assignment):
                var_name = stmt.lvalue.name
                handle_expression(stmt.rvalue)
                slot = get_storage_slot(var_name)
                bytecode.extend([Opcode.PUSH1, int(slot) & 0xff, Opcode.SSTORE])
            elif isinstance(stmt, c_ast.If):
                handle_if_statement(stmt)
            elif isinstance(stmt, c_ast.UnaryOp):
                handle_expression(stmt)

        for node in ast.ext:
            if isinstance(node, c_ast.FuncDef) and node.decl.name == 'main':
                for item in node.body.block_items:
                    handle_statement(item)

        for pos, label in jump_placeholders:
            if label in label_positions:
                jump_target = label_positions[label]
                bytecode[pos] = int(jump_target) & 0xff
            else:
                raise Exception(f"Label not defined: {label}")

        bytecode.append(Opcode.STOP)
        return bytes(bytecode), storage_map
