from block import Block

class Blockchain:
    def __init__(self):
        self.blocks = []
        self.add_genesis_block("first block")

    def add_block(self, block):
        # Add a new block to the blockchain
        self.blocks.append(block)

    def add_genesis_block(self, data):
        # Créer un bloc génèse avec les données initiales
        index = 0
        timestamp = "genesis_timestamp"
        previous_hash = ""
        genesis_block = Block(index, timestamp, data, previous_hash)

        # Ajouter le bloc génèse à la liste des blocs
        self.blocks.append(genesis_block)

    def print_blockchain(self):
        # Print the contents of the blockchain
        for block in self.blocks:
            print(block)

    def get_last_block_index(self):
        # Obtenir l'index du dernier bloc dans la blockchain
        if self.blocks:
            return self.blocks[-1].index
        else:
            # Si la blockchain est vide, retourner -1
            return -1

if __name__ == "__main__": 
    blockchain = Blockchain()
    blockchain.add_genesis_block("Initial data for federated learning")

    # Add more blocks as needed
    block1 = Block(1, "timestamp1", "Block 1 data", blockchain.blocks[-1].current_hash)
    block2 = Block(2, "timestamp2", "Block 2 data", block1.current_hash)

    blockchain.add_block(block1)
    blockchain.add_block(block2)

    # Print the blockchain
    blockchain.print_blockchain()

