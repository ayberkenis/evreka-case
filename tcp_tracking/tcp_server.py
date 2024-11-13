import os
import django
import socket
import threading
import sys
import json

# Add the project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evreka_case1.settings')
django.setup()
# This can't be imported without Django settings module installed
from tcp_tracking.serializers import DeviceDataInputSerializer
from tcp_tracking.tasks import process_tcp_data
HOST = '0.0.0.0'
PORT = 9999

def handle_client_connection(client_socket):
    """
    Handle incoming client connection by reading data from the socket,
    processing it asynchronously, and sending a confirmation back to the client.
    """
    try: 
        # Receive and decode the incoming data
        data = client_socket.recv(1024).decode('utf-8')
        
        try:
            # Parse the data as JSON
            data_json = json.loads(data)
        except json.JSONDecodeError:
            error_message = "Invalid JSON format."
            client_socket.send(b'{"message": "' + error_message.encode('utf-8') + b'"}')
            return

        # Ensure the data is a list for processing
        data_list = data_json if isinstance(data_json, list) else [data_json]

        # Validate the data using the serializer
        serializer = DeviceDataInputSerializer(data=data_list, many=True)
        if serializer.is_valid():
            validated_data = [dict(item) for item in serializer.validated_data]
            
            # Send the validated data to the Celery task
            process_tcp_data.delay(validated_data)

            # Send confirmation back to the client
            client_socket.send(
                b'{"message": "Data received", "data": ' +
                json.dumps(data_list).encode('utf-8') +
                b'}'
            )
        else:
            # Identify missing fields
            required_fields = {'device_id', 'location', 'speed'}
            missing_fields = set()

            for item in data_list:
                if not isinstance(item, dict):
                    continue  # Skip invalid items
                missing_fields.update(required_fields - item.keys())

            if missing_fields:
                message = f"Invalid input data. Missing fields: {', '.join(missing_fields)}"
                client_socket.send(b'{"message": "' + message.encode('utf-8') + b'"}')
            else:
                client_socket.send(b'{"message": "Invalid input data format."}')
    
    except Exception as e:
        # Log and send error back to the client
        print(f"Error processing data: {e}")
        client_socket.send(b'{"message": "There was an error processing the data."}')
    finally:
        # Close the client socket when done
        client_socket.close()

def start_tcp_server():
    """
    Start a TCP server that listens for incoming connections on the specified host and port.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(100) # Listen for 100 connections
    print(f'TCP server listening on {HOST}:{PORT}')

    ### We're keeping the connection open for multiple clients
    ### We also use threading to handle multiple clients concurrently
    while True:
        client_sock, address = server.accept()
        client_handler = threading.Thread(
            target=handle_client_connection,
            args=(client_sock,)
        )
        client_handler.start()

if __name__ == '__main__':
    start_tcp_server()
