import logging
from node import Node
import threading

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    port_node = 5011

    node = Node(node_id="N1", host="localhost", port=port_node, consensus_protocol="pbft")

    while True:
        msg = input("Press yes if you are ready to add nodes: ")
        if msg.lower() == "yes":
            node.add_peer(peer_id="N0", peer_address=("localhost", 5010))
            node.add_peer(peer_id="N2", peer_address=("localhost", 5012))
            break

    threading.Thread(target=node.start_server).start()

    while True:
        msg = input()
        if msg:
            break

    # Afficher la blockchain du nœud
    node.blockchain.print_blockchain()
