import socket
import json

def send_message(host, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        client_socket.send(json.dumps(message).encode())

if __name__ == "__main__":
    while True:
        node = int(input("Choose the node 5010, 5011, 5012: "))

        msg = input("Enter message (or 'q' to quit): ")
        if msg == "q":
            break

        send_message("localhost", node, {"type": "request", "content": msg})
