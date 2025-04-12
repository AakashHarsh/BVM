from bvm.vm import BVM
from state.world_state import WorldState
from compilers.compiler import Compiler
from compilers.c_compiler import CCompiler
from compilers.java_compiler import JavaCompiler
import os

def main():
    print("Starting BVM...")
    # Contract address (can be anything unique per contract)
    contract_address = "contract1"
    
    # Initialize world state and BVM
    world_state = WorldState(storage_file=f'{contract_address}.json')
    vm = BVM(world_state)
    
    # Detect contract language based on file extension
    contract_path = "contracts/math1"  # Base path without extension
    
    if os.path.exists(contract_path + ".py"):
        # Python contract
        print("\nDetected Python contract")
        with open(contract_path + ".py", "r") as f:
            contract_source = f.read()
        
        print("\nCompiling Python contract...")
        bytecode, storage_map = Compiler.compile(contract_source)
    
    elif os.path.exists(contract_path + ".c"):
        # C contract
        print("\nDetected C contract")
        with open(contract_path + ".c", "r") as f:
            contract_source = f.read()
        
        print("\nCompiling C contract...")
        bytecode, storage_map = CCompiler.compile(contract_source)

    elif os.path.exists(contract_path + ".java"):
        # Java contract
        print("\nDetected Java contract")
        with open(contract_path + ".java", "r") as f:
            contract_source = f.read()
        
        print("\nCompiling Java contract...")
        bytecode, storage_map = JavaCompiler.compile(contract_source)
    
    else:
        raise FileNotFoundError("No contract found in contracts/ directory")

    print(f"\nGenerated bytecode: {bytecode.hex()}")
    print(f"Storage mapping: {storage_map}")

    # Deploy contract to the world state
    world_state.set_contract_code(contract_address, bytecode)
    
    # Execute the contract
    print("\nExecuting contract...")
    result = vm.execute(bytecode, address=contract_address)
    if result['success']:
        print(f"Execution successful!")
        print(f"Final storage: {result['storage']}")
        print(f"Total Gas used: {500000 - result['gas_remaining']}")
    else:
        print(f"Execution failed: {result.get('error', 'Unknown error')}")
        print(f"Partial storage: {result.get('storage', {})}")
        print(f"Gas used: {500000 - result['gas_remaining']}")
    

if __name__ == "__main__":
    main()
