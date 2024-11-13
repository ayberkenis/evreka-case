from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.utils.timezone import now
from tcp_tracking.models import DeviceData
from tcp_tracking.tasks import process_tcp_data
from tcp_tracking.serializers import DeviceDataInputSerializer
import json
import socket

class DeviceDataTests(TestCase):
    def setUp(self):
        """
        Set up initial data for testing.
        """
        self.valid_data = [
            {"device_id": "123", "location": "51.5074, -0.1278", "speed": 40},
            {"device_id": "124", "location": "40.7128, -74.0060", "speed": 30}
        ]
        self.invalid_data = [
            {"device_id": "125", "speed": 20},  # Missing location
            {"location": "34.0522, -118.2437", "speed": 25}  # Missing device_id
        ]

    def test_serializer_validation_valid_data(self):
        """
        Test the serializer with valid data.
        """
        serializer = DeviceDataInputSerializer(data=self.valid_data, many=True)
        self.assertTrue(serializer.is_valid())

    def test_serializer_validation_invalid_data(self):
        """
        Test the serializer with invalid data.
        """
        serializer = DeviceDataInputSerializer(data=self.invalid_data, many=True)
        self.assertFalse(serializer.is_valid())

    @patch('tcp_tracking.tasks.DeviceData.objects.bulk_create')
    def test_process_tcp_data_task(self, mock_bulk_create):
        """
        Test the Celery task to process TCP data.
        """
        process_tcp_data(self.valid_data)
        self.assertEqual(mock_bulk_create.call_count, 1)
        self.assertEqual(mock_bulk_create.call_args[0][0][0].device_id, "123")

    def test_process_tcp_data_integration(self):
        """
        Test the integration of processing TCP data and saving to the database.
        """
        process_tcp_data(self.valid_data)
        self.assertEqual(DeviceData.objects.count(), len(self.valid_data))
        self.assertEqual(DeviceData.objects.first().device_id, "123")

class TCPServerTests(TestCase):
    def setUp(self):
        """
        Set up initial data for TCP server tests.
        """
        self.valid_data = [
            {"device_id": "123", "location": "51.5074, -0.1278", "speed": 40},
            {"device_id": "124", "location": "40.7128, -74.0060", "speed": 30}
        ]
        self.invalid_data = [
            {"device_id": "125", "speed": 20},  # Missing location
            {"location": "34.0522, -118.2437", "speed": 25}  # Missing device_id
        ]
        
    @patch('tcp_tracking.tasks.process_tcp_data.delay')
    def test_handle_client_connection_valid_data(self, mock_process_tcp_data):
        """
        Test handling client connection with valid data.
        """
        mock_client_socket = MagicMock()
        
        # Simulate valid JSON data
        data = json.dumps(self.valid_data)
        mock_client_socket.recv.return_value = data.encode('utf-8')

        # Call the server's client handler
        from .tcp_server import handle_client_connection
        handle_client_connection(mock_client_socket)

        # Verify data was sent to Celery task
        mock_process_tcp_data.assert_called_once_with(self.valid_data)

        # Check the response sent back to the client
        response = mock_client_socket.send.call_args[0][0]
        response_data = json.loads(response.decode('utf-8'))
        self.assertIn("message", response_data)
        self.assertEqual(response_data["message"], "Data received")


    @patch('socket.socket')
    def test_handle_client_connection_invalid_data(self, mock_socket):
        """
        Test handling client connection with invalid data.
        """
        mock_client_socket = MagicMock()
        mock_socket.return_value = mock_client_socket

        data = json.dumps(self.invalid_data)
        mock_client_socket.recv.return_value = data.encode('utf-8')

        from .tcp_server import handle_client_connection
        handle_client_connection(mock_client_socket)

        response = mock_client_socket.send.call_args[0][0]
        response_data = json.loads(response.decode('utf-8'))
        self.assertIn("message", response_data)
        self.assertIn("Invalid input data", response_data["message"])

    @patch('socket.socket')
    def test_handle_client_connection_invalid_json(self, mock_socket):
        """
        Test handling client connection with invalid JSON.
        """
        mock_client_socket = MagicMock()
        mock_socket.return_value = mock_client_socket

        data = "{invalid_json:}"
        mock_client_socket.recv.return_value = data.encode('utf-8')

        from .tcp_server import handle_client_connection
        handle_client_connection(mock_client_socket)

        response = mock_client_socket.send.call_args[0][0]
        response_data = json.loads(response.decode('utf-8'))
        self.assertIn("message", response_data)
        self.assertEqual(response_data["message"], "Invalid JSON format.")
