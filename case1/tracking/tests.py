from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import DeviceData

class DeviceDataTests(APITestCase):
    def test_post_data(self):
        url = reverse('device_data')
        data = {'device_id': '123', 'location': 'X', 'speed': '50.0'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_get_latest_data(self):
        DeviceData.objects.create(device_id='123', location='X', speed='50.0')
        url = reverse('latest_device_data', args=['123'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)