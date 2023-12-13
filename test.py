import logging
from node import Node
import threading

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":

    port_node_1 = 5010
    port_node_2 = 5011
    port_node_3 = 5012

    node1 = Node(node_id="N0", host="localhost", port=port_node_1, consensus_protocol="pbft")
    node2 = Node(node_id="N1", host="localhost", port=port_node_2, consensus_protocol="pbft")
    node3 = Node(node_id="N2", host="localhost", port=port_node_3, consensus_protocol="pbft")

    node1.add_peer(peer_id="N1", peer_address=("localhost", port_node_2), public_key=node2.public_key)
    node1.add_peer(peer_id="N2", peer_address=("localhost", port_node_3), public_key=node3.public_key)

    node2.add_peer(peer_id="N0", peer_address=("localhost", port_node_1), public_key=node1.public_key)
    node2.add_peer(peer_id="N2", peer_address=("localhost", port_node_3), public_key=node3.public_key)

    node3.add_peer(peer_id="N0", peer_address=("localhost", port_node_1), public_key=node1.public_key)
    node3.add_peer(peer_id="N1", peer_address=("localhost", port_node_2), public_key=node2.public_key)

    threading.Thread(target=node1.start_server).start()
    threading.Thread(target=node2.start_server).start()
    threading.Thread(target=node3.start_server).start()

    while True: 
        msg = input()
        if msg != "q":
            message_from_node1 = {"type": "request", "content": msg}
            node2.send_message(peer_id="N0", message=message_from_node1)
        else: 
            break

    node1.blockchain.print_blockchain()
    node2.blockchain.print_blockchain()
    node3.blockchain.print_blockchain()