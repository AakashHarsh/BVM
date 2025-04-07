class WorldState:
    def __init__(self):
        self.accounts = {}
    
    def create_account(self, address):
        if address not in self.accounts:
            self.accounts[address] = {
                'balance': 0,
                'storage': {},
                'code': b''
            }
    
    def set_contract_code(self, address, code):
        self.create_account(address)
        self.accounts[address]['code'] = code
    
    def get_contract_code(self, address):
        return self.accounts.get(address, {}).get('code', b'')
