# test.py
from node import Node
import threading

if __name__ == "__main__":

    port_node_1 = 5002
    port_node_2 = 5003

    node1 = Node(node_id="N0", host="localhost", port=port_node_1, consensus_protocol="pbft")
    node2 = Node(node_id="N1", host="localhost", port=port_node_2, consensus_protocol="pbft")

    node1.add_peer(peer_id="N1", peer_address=("localhost", port_node_2))
    node2.add_peer(peer_id="N0", peer_address=("localhost", port_node_1))

    threading.Thread(target=node1.start_server).start()
    threading.Thread(target=node2.start_server).start()

    message_from_node1 = {"type": "request", "message": "Hello from Tanguy"}

    node2.send_message(peer_id="N0", message=message_from_node1)