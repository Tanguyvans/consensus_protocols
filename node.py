import socket
import threading
import json

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

import base64

from pbft_protocol import PBFTProtocol
from consensus_protocol import ConsensusProtocol
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

        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

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

    def add_peer(self, peer_id, peer_address, public_key):
        self.peers[peer_id] = {"address": peer_address, "public_key": public_key}

