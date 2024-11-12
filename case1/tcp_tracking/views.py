from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DeviceData
from .serializers import DeviceDataSerializer

class DeviceDataListAPI(APIView):
    def get(self, request):
        # TODO: implement GET method
        pass

class LatestDeviceDataAPI(APIView):
    def get(self, request, device_id):
        # TODO: implement latest GET method
        pass
