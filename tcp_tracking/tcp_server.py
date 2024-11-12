import os
import django
import socket
import threading
import sys
# Add the project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evreka_case1.settings')
django.setup()
# This can't be imported without Django settings module installed
from tcp_tracking.tasks import process_tcp_data
HOST = '0.0.0.0'
PORT = 9999

def handle_client_connection(client_socket):
    """
    Handle incoming client connection by reading data from the socket, processing it asynchronously, and sending a confirmation back to the client.
    """
    try: 
        # Decode the incoming data
        data = client_socket.recv(1024).decode('utf-8')
        # Process the data asynchronously
        process_tcp_data.delay(data)
        # Send confirmation back to the client
        client_socket.send(b'Data received')
    except Exception as e:
        print(f'Error processing data: {e}')
        client_socket.send(b'There was an error proccessing the data. ')
    finally:
        # Close the client socket when done
        client_socket.close()

def start_tcp_server():
    """
    Start a TCP server that listens for incoming connections on the specified host and port.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(100)
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
