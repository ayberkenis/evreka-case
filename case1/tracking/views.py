from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import DeviceDataSerializer
from .tasks import process_device_data
from .models import DeviceData

class DeviceDataAPI(APIView):
    def post(self, request):
        data = request.data
        # Send data to the Celery worker
        process_device_data.delay(data)
        return Response({'message': 'Data received'}, status=status.HTTP_202_ACCEPTED)

class DeviceDataListAPI(APIView):
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        device_id = request.query_params.get('device_id')

        queryset = DeviceData.objects.all()

        if device_id:
            queryset = queryset.filter(device_id=device_id)
        if start_date and end_date:
            queryset = queryset.filter(timestamp__range=[start_date, end_date])

        serializer = DeviceDataSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LatestDeviceDataAPI(APIView):
    def get(self, request, device_id):
        data = DeviceData.objects.filter(device_id=device_id).order_by('-timestamp').first()
        if data:
            serializer = DeviceDataSerializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No data found'}, status=status.HTTP_404_NOT_FOUND)
