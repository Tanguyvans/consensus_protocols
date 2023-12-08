import socket
import threading
import json

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
            peer_address = self.peers[peer_id]
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(peer_address)
            client_socket.send(json.dumps(message).encode())
            client_socket.close()
        else:
            print(f"Peer {peer_id} not found.")

    def add_peer(self, peer_id, peer_address):
        self.peers[peer_id] = peer_address
