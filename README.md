# Blockchain Virtual Machine (BVM)

A Python-based virtual machine for executing smart contract bytecode, supporting Python and C-like contracts.

## Features
- Compiles Python/C contracts/ Java Contracts to custom bytecode
- EVM-inspired architecture with gas accounting
- Supports:
  - Arithmetic/logic operations
  - Conditional statements (`if/else`)
  - Loops (`while`, `for`)
  - Persistent storage

## Quick Start

### Prerequisites
- OS: Linux
- Python 3.8+
- `pycparser` (for C contracts):  
  ```bash
  pip install pycparser


### Clone repository
  ```bash
git clone https://github.com/AakashHarsh/BVM.git
cd BVM/bvm_project

### Run the BVM
```bash
python3 main.py 
