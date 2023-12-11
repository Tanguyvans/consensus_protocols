from block import Block
from consensus_protocol import ConsensusProtocol

class PBFTProtocol(ConsensusProtocol):
    def __init__(self, node, blockchain):
        self.node = node
        self.node_id = self.node.node_id

        self.prepare_counts = {}
        self.commit_counts = {}

        self.blockchain = blockchain

    def handle_message(self, message):
        message_type = message.get("type")

        if message_type == "request":
            self.request(message["message"])
        elif message_type == "pre-prepare":
            self.pre_prepare(message["block"])
        elif message_type == "prepare":
            self.prepare(message["block"])
        elif message_type == "commit":
            self.commit(message["block"])
        else:
            print(f"Unknown message type: {message_type}")

    def request(self, content):
        # Implémentez la logique de la phase request pour PBFT
        print(f"Node {self.node_id} received request with content: {content}")
        # Créez un bloc à partir de la demande et déclenchez la phase pre-prepare
        block = self.create_block_from_request(content)

        message = {"type": "pre-prepare", "block": block.to_dict()}
        self.node.broadcast_message(message)
        self.handle_message(message)

    def pre_prepare(self, message):
        print(f"Node {self.node_id} received pre-prepare for block: \n{message}")

        block = Block(message["index"], message["timestamp"], message["data"], message["previous_hash"])

        self.prepare_counts[message["current_hash"]] = 0

        message = {"type": "prepare", "block": block.to_dict()}
        self.node.broadcast_message(message)

    def prepare(self, message):
        print(f"Node {self.node_id} received prepare for block {message}")
        block_hash = message["current_hash"]
        if block_hash not in self.prepare_counts: 
            self.prepare_counts[block_hash] = 0
        self.prepare_counts[block_hash] += 1

        if self.is_prepared(block_hash): 
            commit_message = {"type": "commit", "block": message}
            self.node.broadcast_message(commit_message)
            print(f"Node {self.node_id} prepared block to {self.node.peers}")
        else:
            print(f"Node {self.node_id} waiting for more prepares for block {block_hash}")

    def commit(self, block_data):
        print(f"Node {self.node_id} received commit for block {block_data}")
        block_hash = block_data["current_hash"]

        if block_hash not in self.commit_counts: 
            self.commit_counts[block_hash] = 0
        self.commit_counts[block_hash] += 1

        if self.can_commit(block_hash):
            print(f"Node {self.node_id} committing block {block_hash}")

            # Ajoutez le bloc à la blockchain
            if self.validate_block(block_data):
                block = Block(
                    index=block_data["index"],
                    timestamp=block_data["timestamp"],
                    data=block_data["data"],
                    previous_hash=block_data["previous_hash"]
                )
                self.blockchain.add_block(block)
                print(f"Node {self.node_id} committed block {block_hash}")
            else:
                print("Invalid block. Discarding commit.")
        else:
            print(f"Node {self.node_id} waiting for more commits for block {block_hash}")

    def validate_block(self, block_data):
        # Vérifiez l'intégrité du bloc
        if "index" not in block_data or "timestamp" not in block_data \
                or "data" not in block_data or "previous_hash" not in block_data:
            return False

        # Vérifiez que l'index est correctement incrémenté
        if block_data["index"] != len(self.blockchain.blocks):
            return False

        # Vérifiez la validité du hachage précédent
        previous_block = self.blockchain.blocks[-1] if self.blockchain.blocks else None
        if previous_block and block_data["previous_hash"] != previous_block.current_hash:
            return False

        # Vous pouvez ajouter d'autres vérifications selon les besoins (par exemple, vérification de la signature)

        return True

    def create_block_from_request(self, content):
        previous_blocks = self.blockchain.blocks
        index_of_new_block = len(previous_blocks)
        timestamp_of_new_block = "timestamp_of_new_block"
        previous_hash_of_last_block = previous_blocks[-1].current_hash

        # Créez un nouveau bloc à partir de la demande du client
        new_block = Block(index_of_new_block, timestamp_of_new_block, content, previous_hash_of_last_block)

        return new_block
    
    def is_prepared(self, id):
        return self.prepare_counts[id] >= 2

    def can_commit(self, id):
        return self.commit_counts[id] >= 2

