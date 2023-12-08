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


    def commit(self, message):
        print(f"Node {self.node_id} received commit for block {message}")
        block_hash = message["current_hash"]

        if block_hash not in self.commit_counts: 
            self.commit_counts[block_hash] = 0
        self.commit_counts[block_hash] += 1

        if self.can_commit(block_hash): 
            print("COMMITING")


    def create_block_from_request(self, content):
        previous_blocks = self.blockchain.blocks
        index_of_new_block = len(previous_blocks)
        timestamp_of_new_block = "timestamp_of_new_block"
        previous_hash_of_last_block = previous_blocks[-1].current_hash

        # Créez un nouveau bloc à partir de la demande du client
        new_block = Block(index_of_new_block, timestamp_of_new_block, content, previous_hash_of_last_block)

        return new_block
    
    def is_prepared(self, id):
        return self.prepare_counts[id] >= 1

    def can_commit(self, id):
        return self.commit_counts[id] >= 1

