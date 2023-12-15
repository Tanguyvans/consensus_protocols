import socket
import threading
import json
import os
import time

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

import base64

from protocols.pbft_protocol import PBFTProtocol
from protocols.raft_protocol import RaftProtocol
from protocols.consensus_protocol import ConsensusProtocol
from blockchain import Blockchain
from block import Block

class Node:
    def __init__(self, node_id, host, port, consensus_protocol):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.peers = {}

        self.blockchain = Blockchain()

        if consensus_protocol == "pbft": 
            self.consensus_protocol = PBFTProtocol(node=self, blockchain=self.blockchain)
        elif consensus_protocol == "raft": 
            self.consensus_protocol = RaftProtocol(node=self, blockchain=self.blockchain)
            threading.Thread(target=self.consensus_protocol.run).start()

        private_key_path = f"keys/{node_id}_private_key.pem"
        public_key_path = f"keys/{node_id}_public_key.pem"

        self.getKeys(private_key_path, public_key_path)

    def sign_message(self, message):
        signature = self.private_key.sign(
            json.dumps(message).encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode()

    def verify_signature(self, signature, message, public_key):
        try:
            signature_binary = base64.b64decode(signature)

            public_key.verify(
                signature_binary,
                json.dumps(message).encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            print(f"Signature verification error: {e}")
            return False

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Node {self.node_id} listening on {self.host}:{self.port}")

        while True:
            client_socket, addr = server_socket.accept()
            threading.Thread(target=self.handle_message, args=(client_socket,)).start()

    def handle_message(self, client_socket):
        data = client_socket.recv(1024)
        message = json.loads(data.decode())
        self.consensus_protocol.handle_message(message)

        client_socket.close()

    def broadcast_message(self, message):

        for peer_id in self.peers:
            self.send_message(peer_id, message)

    def send_message(self, peer_id, message):
        if peer_id in self.peers:
            peer_info = self.peers[peer_id]
            peer_address = peer_info["address"]

            signed_message = message.copy()
            signed_message["signature"] = self.sign_message(signed_message)
            signed_message["id"] = self.node_id

            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(peer_address)
            client_socket.send(json.dumps(signed_message).encode())
            client_socket.close()
        else:
            print(f"Peer {peer_id} not found.")

    def add_peer(self, peer_id, peer_address):
        with open(f"keys/{peer_id}_public_key.pem", 'rb') as f:
            public_key = serialization.load_pem_public_key(
                f.read(),
                backend=default_backend()
            )

        self.peers[peer_id] = {"address": peer_address, "public_key": public_key}

    def getKeys(self, private_key_path, public_key_path): 
        if os.path.exists(private_key_path) and os.path.exists(public_key_path):
            with open(private_key_path, 'rb') as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )

            with open(public_key_path, 'rb') as f:
                self.public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
        else:
            # Generate new keys
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            self.public_key = self.private_key.public_key()

            # Save keys to files
            with open(private_key_path, 'wb') as f:
                f.write(self.private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))

            with open(public_key_path, 'wb') as f:
                f.write(self.public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))

if __name__ == "__main__":
    port_node_1 = 5010
    port_node_2 = 5011
    port_node_3 = 5012

    node1 = Node(node_id="N0", host="localhost", port=port_node_1, consensus_protocol="raft")
    node2 = Node(node_id="N1", host="localhost", port=port_node_2, consensus_protocol="raft")
    node3 = Node(node_id="N2", host="localhost", port=port_node_3, consensus_protocol="raft")

    node1.add_peer(peer_id="N1", peer_address=("localhost", port_node_2))
    node1.add_peer(peer_id="N2", peer_address=("localhost", port_node_3))

    node2.add_peer(peer_id="N0", peer_address=("localhost", port_node_1))
    node2.add_peer(peer_id="N2", peer_address=("localhost", port_node_3))

    node3.add_peer(peer_id="N0", peer_address=("localhost", port_node_1))
    node3.add_peer(peer_id="N1", peer_address=("localhost", port_node_2))

    threading.Thread(target=node1.start_server).start()
    threading.Thread(target=node2.start_server).start()
    threading.Thread(target=node3.start_server).start()


    time.sleep(20)

    print("client sending")
    message_from_node1 = {"type": "client_request", "content": "hello"}
    node2.send_message(peer_id="N0", message=message_from_node1)

    time.sleep(5)
    message_from_node1 = {"type": "client_request", "content": "testing"}
    node1.send_message(peer_id="N1", message=message_from_node1)

    time.sleep(5)
    message_from_node1 = {"type": "client_request", "content": "tanguy"}
    node2.send_message(peer_id="N0", message=message_from_node1)

    time.sleep(5)
    print(node1.consensus_protocol.log)
    print(node2.consensus_protocol.log)
    print(node3.consensus_protocol.log)