from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from .serializers import DeviceDataSerializer
from .tasks import process_device_data
from .models import DeviceData
from .serializers import DeviceDataInputSerializer
from django.core.exceptions import ValidationError
from .exceptions import InvalidTimeException

class DeviceDataAPI(APIView):
   """
    API view to receive device data and process it asynchronously.

    Attributes:
    serializer_class (DeviceDataInputSerializer): The serializer class used for validating and serializing the device data.
    Methods:
    post(request):
    Handles POST requests to receive device data and process it asynchronously.
    Args:
    request (Request): The request object containing the device data.
    Returns:
    Response: A response with a message indicating that data has been received or a response with errors if the data is invalid.
   
   """
   def post(self, request):
        data_list = request.data if isinstance(request.data, list) else [request.data]
        serializer = DeviceDataInputSerializer(data=data_list, many=True)
        if serializer.is_valid():
            # Convert each item in validated_data to a dict
            validated_data = [dict(item) for item in serializer.validated_data]
            process_device_data.delay(validated_data)
            return Response({'message': 'Data received'}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeviceDataListAPI(GenericAPIView):
    """
    API view to retrieve a list of device data with optional filtering by device ID and date range.
    Attributes:
        serializer_class (DeviceDataSerializer): The serializer class used for serializing the device data.
        pagination_class (PageNumberPagination): The pagination class used for paginating the device data.
    Methods:
        get(request):
            Handles GET requests to retrieve the list of device data.
            Args:
                request (Request): The request object containing query parameters for filtering.
            Returns:
                Response: A paginated response with serialized device data or a response with serialized device data.
        get_queryset(request):
            Retrieves the queryset of device data with optional filtering by device ID and date range.
            Args:
                request (Request): The request object containing query parameters for filtering.
            Returns:
                QuerySet: A queryset of filtered device data ordered by timestamp in descending order.
    """
    serializer_class = DeviceDataSerializer
    pagination_class = PageNumberPagination

    def get(self, request):
        try:
            queryset = self.get_queryset(request)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except InvalidTimeException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def get_queryset(self, request):
        try:
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            device_id = request.query_params.get('device_id')

            queryset = DeviceData.objects.all()

            if device_id:
                queryset = queryset.filter(device_id=device_id)
            if start_date and end_date:
                queryset = queryset.filter(timestamp__range=[start_date, end_date])

            return queryset.order_by('-timestamp').only('device_id', 'location', 'speed', 'timestamp')
        except ValidationError as e:

            raise InvalidTimeException(f'Invalid time format: {e}')

class LatestDeviceDataAPI(APIView):


    def get(self, request, device_id):
        data = DeviceData.objects.filter(device_id=device_id).order_by('-timestamp').first()
        if data:
            serializer = DeviceDataSerializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No data found'}, status=status.HTTP_404_NOT_FOUND)