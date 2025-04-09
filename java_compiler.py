from bvm.opcodes import Opcode
import re

class JavaCompiler:
    @staticmethod
    def compile(source_code):
        """Compile Java-like code to BVM bytecode with full operation support"""
        bytecode = bytearray()
        storage_map = {}
        variables = {}
        
        # Clean and prepare source
        lines = []
        for line in source_code.split('\n'):
            line = line.strip()
            if '//' in line:
                line = line.split('//')[0]
            if line and not line.startswith(('/*', '*')):
                lines.append(line)
        clean_source = ' '.join(lines)
        
        # Extract all variable declarations
        var_declarations = re.findall(r'(int\s+\w+\s*=\s*\d+)', clean_source)
        for decl in var_declarations:
            parts = decl.split('=')
            var_name = parts[0].replace('int', '').strip()
            value = parts[1].strip()
            try:
                variables[var_name] = int(value)
            except ValueError:
                variables[var_name] = 0
        
        # Add if/else handling
        if_pattern = r'if\s*\(([^)]+)\)\s*\{([^}]*)\}\s*else\s*\{([^}]*)\}'
        if_matches = re.findall(if_pattern, clean_source)

        for condition, if_block, else_block in if_matches:
            condition = condition.strip()
            
            # Compile the condition
            if '<=' in condition:
                a, b = condition.split('<=')
                comparison_opcode = Opcode.LTE
                need_invert = False
            elif '>=' in condition:
                a, b = condition.split('>=')
                comparison_opcode = Opcode.GTE
                need_invert = False
            elif '==' in condition:
                a, b = condition.split('==')
                comparison_opcode = Opcode.EQ
                need_invert = False
            elif '!=' in condition:
                a, b = condition.split('!=')
                comparison_opcode = Opcode.EQ
                need_invert = True
            elif '<' in condition:
                a, b = condition.split('<')
                comparison_opcode = Opcode.LT
                need_invert = False
            elif '>' in condition:
                a, b = condition.split('>')
                comparison_opcode = Opcode.GT
                need_invert = False
            else:
                # Just a variable or value - check if not zero
                a = condition
                b = None
                comparison_opcode = None
                need_invert = False
            
            # Push operands and apply comparison if we have one
            if comparison_opcode:
                a = a.strip()
                b = b.strip()
                
                # Push operands in correct order
                if a in variables:
                    bytecode.extend([Opcode.PUSH1, variables[a]])
                else:
                    try:
                        bytecode.extend([Opcode.PUSH1, int(a)])
                    except ValueError:
                        bytecode.extend([Opcode.PUSH1, 0])
                
                if b in variables:
                    bytecode.extend([Opcode.PUSH1, variables[b]])
                else:
                    try:
                        bytecode.extend([Opcode.PUSH1, int(b)])
                    except ValueError:
                        bytecode.extend([Opcode.PUSH1, 0])
                
                # Apply comparison
                bytecode.append(comparison_opcode)
                
                # Invert if needed (for != operation)
                if need_invert:
                    bytecode.append(Opcode.ISZERO)
                bytecode.append(Opcode.ISZERO)
            else:
                # Just push the value for direct condition check
                if a in variables:
                    bytecode.extend([Opcode.PUSH1, variables[a]])
                else:
                    try:
                        bytecode.extend([Opcode.PUSH1, int(a)])
                    except ValueError:
                        bytecode.extend([Opcode.PUSH1, 0])
            
            # Add placeholder for jump to else block if condition is false
            bytecode.append(Opcode.PUSH1)
            else_jump_pos = len(bytecode)
            bytecode.append(0)  # Placeholder
            bytecode.append(Opcode.JUMPI)
            
            # Compile the if block
            if_block_code = []
            if_var_declarations = re.findall(r'(int\s+\w+\s*=\s*[^;]+;)', if_block)
            for decl in if_var_declarations:
                decl = decl.strip()
                if decl.startswith('int '):
                    parts = decl.split('=')
                    var_name = parts[0].replace('int', '').strip()
                    value = parts[1].replace(';', '').strip()
                    
                    # Push value
                    try:
                        val = int(value)
                        if_block_code.extend([Opcode.PUSH1, val])
                    except ValueError:
                        if value in variables:
                            if_block_code.extend([Opcode.PUSH1, variables[value]])
                        else:
                            if_block_code.extend([Opcode.PUSH1, 0])
                    
                    # Store to storage
                    storage_key = hash(var_name) % 256
                    storage_map[var_name] = storage_key
                    if_block_code.extend([
                        Opcode.PUSH1, storage_key,
                        Opcode.SSTORE
                    ])
            
            bytecode.extend(if_block_code)
            
            # Jump to end after if block
            bytecode.append(Opcode.PUSH1)
            end_jump_pos = len(bytecode)
            bytecode.append(0)  # Placeholder
            bytecode.append(Opcode.JUMP)
            
            # Else block starts here
            else_start_pos = len(bytecode)
            bytecode.append(Opcode.JUMPDEST)
            
            # Compile the else block
            else_block_code = []
            else_var_declarations = re.findall(r'(int\s+\w+\s*=\s*[^;]+;)', else_block)
            for decl in else_var_declarations:
                decl = decl.strip()
                if decl.startswith('int '):
                    parts = decl.split('=')
                    var_name = parts[0].replace('int', '').strip()
                    value = parts[1].replace(';', '').strip()
                    
                    # Push value
                    try:
                        val = int(value)
                        else_block_code.extend([Opcode.PUSH1, val])
                    except ValueError:
                        if value in variables:
                            else_block_code.extend([Opcode.PUSH1, variables[value]])
                        else:
                            else_block_code.extend([Opcode.PUSH1, 0])
                    
                    # Store to storage
                    storage_key = hash(var_name) % 256
                    storage_map[var_name] = storage_key
                    else_block_code.extend([
                        Opcode.PUSH1, storage_key,
                        Opcode.SSTORE
                    ])
            
            bytecode.extend(else_block_code)
            
            # End of if/else
            end_pos = len(bytecode)
            bytecode.append(Opcode.JUMPDEST)
            
            # Update jump destinations - FIXED
            # Calculate the correct jump destinations (absolute positions)
            bytecode[else_jump_pos] = else_start_pos
            bytecode[end_jump_pos] = end_pos
        
        # Process all operations outside if/else blocks
        operations = re.findall(r'(\w+\s*=\s*[^;]+;)', clean_source)
        for op in operations:
            try:
                op = op.replace(';', '').strip()
                parts = op.split('=', 1)
                if len(parts) != 2:
                    continue
                    
                var_name, expr = parts
                var_name = var_name.strip()
                expr = expr.strip()
                
                # Handle special cases first
                if expr.startswith('!'):
                    operand = expr[1:].strip()
                    if operand in variables:
                        bytecode.extend([
                            Opcode.PUSH1, variables[operand],
                            Opcode.ISZERO
                        ])
                elif '!=' in expr:
                    a, b = expr.split('!=')
                    a = a.strip()
                    b = b.strip()
                    if a in variables and b in variables:
                        bytecode.extend([
                            Opcode.PUSH1, variables[a],
                            Opcode.PUSH1, variables[b],
                            Opcode.EQ,
                            Opcode.ISZERO
                        ])
                else:
                    # Handle all other operations
                    if '+' in expr:
                        a, b = expr.split('+')
                        opcode = Opcode.ADD
                    elif '-' in expr:
                        a, b = expr.split('-')
                        opcode = Opcode.SUB
                    elif '*' in expr:
                        a, b = expr.split('*')
                        opcode = Opcode.MUL
                    elif '/' in expr:
                        a, b = expr.split('/')
                        opcode = Opcode.DIV
                    elif '%' in expr:
                        a, b = expr.split('%')
                        opcode = Opcode.MOD
                    elif '<=' in expr:
                        a, b = expr.split('<=')
                        opcode = Opcode.LTE
                    elif '>=' in expr:
                        a, b = expr.split('>=')
                        opcode = Opcode.GTE
                    elif '==' in expr:
                        a, b = expr.split('==')
                        opcode = Opcode.EQ
                    elif '<' in expr:
                        a, b = expr.split('<')
                        opcode = Opcode.LT
                    elif '>' in expr:
                        a, b = expr.split('>')
                        opcode = Opcode.GT
                    else:
                        continue
                    
                    a = a.strip()
                    b = b.strip()
                    if a in variables and b in variables:
                        bytecode.extend([
                            Opcode.PUSH1, variables[a],
                            Opcode.PUSH1, variables[b],
                            opcode
                        ])
                
                # Store result if we processed an operation
                if len(bytecode) > 0 and bytecode[-1] != Opcode.SSTORE:
                    storage_key = hash(var_name) % 256
                    storage_map[var_name] = storage_key
                    bytecode.extend([
                        Opcode.PUSH1, storage_key,
                        Opcode.SSTORE
                    ])
            
            except Exception as e:
                print(f"Warning: Could not compile operation '{op}': {str(e)}")
                continue
                
        # Always end with STOP
        if len(bytecode) == 0 or bytecode[-1] != Opcode.STOP:
            bytecode.append(Opcode.STOP)
            
        return bytes(bytecode), storage_map