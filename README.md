# Blockchain Virtual Machine (BVM)

A Python-based virtual machine for executing smart contract bytecode, supporting Python and C-like contracts.

## Features
- Compiles Python/ C/ Java/ CPP/ JS Contracts to custom bytecode
- EVM-inspired architecture with gas accounting
- Supports:
  - Arithmetic/logic operations
  - Conditional statements (`if/else`)
  - Loops (`while`, `for`)
  - Persistent storage

## Quick Run
```bash
cd BVM/bvm_project
python3 -m venv venv
source venv/bin/activate
pip install pycparser
pip install javalang
pip install esprima
python3 main.py contracts/math1.py contract2 500000
```

## Detailed Steps
### Prerequisites
- OS: Linux
- Python 3.8+
- `pycparser` (for C contracts):  
  ```bash
  pip install pycparser
- `javalang` (for Java contracts):  
  ```bash
  pip install javalang
- `esprima` (for JavaScript contracts):  
  ```bash
  pip install esprima

### Move inside bvm_project directory
```bash
cd BVM/bvm_project
```

### Run the BVM
```bash
python3 main.py <contract_path> <address> <gas_limit>
```
Command Arguments

| Argument        | Required | Description                          | Example           |
|----------------|----------|--------------------------------------|-------------------|
| `contract_path` | Yes      | Path to contract file with extension | `contracts/math.c` |
| `address`       | Yes      | Unique contract identifier           | `contract1`        |
| `gas_limit`     | Yes      | Maximum gas for execution (integer)  | `500000`           |

### Example usage
```bash
python3 main.py contracts/math1.py contract2 500000
```
Similarly C, Java, CPP and JS contracts can be executed just by replacing contracts/math1.py with the path to corresponding C or java or CPP or JS file respectively.

## Execution Output Example

```text
Starting BVM with contract 'contract2'...

Detected Python contract
Compiling contract...
Slot 151 assigned to 'a'
Slot 35 assigned to 'b'
Slot 245 assigned to 'sum'

Generated bytecode: 600560975560066023556097546023540160f55500
Storage mapping: {'a': 151, 'b': 35, 'sum': 245}

Executing contract...
Executing PUSH1 at pc=0, Gas used: 3
Executing PUSH1 at pc=2, Gas used: 3
Executing SSTORE at pc=4, Gas used: 5000
Executing PUSH1 at pc=5, Gas used: 3
Executing PUSH1 at pc=7, Gas used: 3
Executing SSTORE at pc=9, Gas used: 5000
Executing PUSH1 at pc=10, Gas used: 3
Executing SLOAD at pc=12, Gas used: 200
Executing PUSH1 at pc=13, Gas used: 3
Executing SLOAD at pc=15, Gas used: 200
Executing ADD at pc=16, Gas used: 3
Executing PUSH1 at pc=17, Gas used: 3
Executing SSTORE at pc=19, Gas used: 5000
Executing STOP at pc=20, Gas used: 0

Execution Results:
Contract: contract2
Status: Success
Gas used: 15424/500000
Final and previous storage state: 
{151: 5, 35: 6, 245: 11}
