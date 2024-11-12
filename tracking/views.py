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
from dateutil.parser import parse
from datetime import datetime

class DeviceDataAPI(APIView):
    """
    post:
    Receive device data and process it asynchronously.

    Accepts device data in JSON format (single object or array). The data is validated and passed
    to a background task for processing.

    Parameters:
        - data (list or dict): A single device data object or an array of objects.

    Responses:
        202: Data successfully received and queued for processing.
        400: Invalid input data.
    """
    def post(self, request):
        data_list = request.data if isinstance(request.data, list) else [request.data]
        serializer = DeviceDataInputSerializer(data=data_list, many=True)
        if serializer.is_valid():
            # Convert each item in validated_data to a dict
            validated_data = [dict(item) for item in serializer.validated_data]
            process_device_data.delay(validated_data)
            return Response({'message': 'Data received', 'data': validated_data}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeviceDataListAPI(GenericAPIView):
    """
    get:
    Retrieve a paginated list of device data.

    Allows optional filtering by `device_id` and/or a date range (`start_date`, `end_date`).

    Parameters:
        - device_id (str): Filter results by device ID.
        - start_date (str): Filter results starting from this date (inclusive).
        - end_date (str): Filter results up to this date (inclusive).

    Responses:
        200: List of device data.
        400: Invalid input parameters.
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

            def parse_date(date_string):
                if not date_string:
                    return None
                try:
                    # Parse date using `dateutil.parser`
                    return parse(date_string).date()
                except ValueError:
                    raise InvalidTimeException(f"Invalid date format: {date_string}")
                
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)
            
            if end_date:
                end_date = datetime.combine(end_date, datetime.max.time())

            if device_id:
                queryset = queryset.filter(device_id=device_id)
            if start_date and end_date:
                queryset = queryset.filter(timestamp__range=[start_date, end_date])

            return queryset.order_by('-timestamp').only('device_id', 'location', 'speed', 'timestamp')
        except ValidationError as e:

            raise InvalidTimeException(f'Invalid time format: {e}')

class LatestDeviceDataAPI(APIView):

    """
    get:
    Retrieve the latest device data for a specific device ID.

    Parameters:
        - device_id (str): The ID of the device to retrieve the latest data for.

    Responses:
        200: The latest device data for the given device ID.
        404: No data found for the given device ID.
    """
    def get(self, request, device_id):
        data = DeviceData.objects.filter(device_id=device_id).order_by('-timestamp').first()
        if data:
            serializer = DeviceDataSerializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No data found'}, status=status.HTTP_404_NOT_FOUND)