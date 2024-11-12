import socket
import threading
from .tasks import process_tcp_data

HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 9999       # TCP port number

def handle_client_connection(client_socket):
    data = client_socket.recv(1024).decode('utf-8')
    # Process data asynchronously using Celery
    process_tcp_data.delay(data)
    client_socket.send(b'Data received')
    client_socket.close()

def start_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(100)  # Maximum number of queued connections
    print(f'TCP server listening on {HOST}:{PORT}')
    while True:
        client_sock, address = server.accept()
        client_handler = threading.Thread(
            target=handle_client_connection,
            args=(client_sock,)
        )
        client_handler.start()

if __name__ == '__main__':
    start_tcp_server()
