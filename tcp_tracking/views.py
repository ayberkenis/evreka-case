from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from .models import DeviceData
from .exceptions import InvalidTimeException
from dateutil.parser import parse
from datetime import datetime
from .serializers import DeviceDataInputSerializer
from django.core.exceptions import ValidationError

class DeviceDataListAPI(GenericAPIView):
    """
        Returns a list of device data based on the query parameters.
        [Paginated]
    """
    serializer_class = DeviceDataInputSerializer
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
        """
        Retrieves a list of device data based on the query parameters.
        """
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
    Retrieves the latest device data for a specific device ID.
    """
    def get(self, request, device_id):
        data = DeviceData.objects.filter(device_id=device_id).order_by('-timestamp').first()
        if data:
            serializer = DeviceDataInputSerializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No data found'}, status=status.HTTP_404_NOT_FOUND)