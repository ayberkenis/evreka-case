from celery import shared_task
import json
from .models import DeviceData

@shared_task
def process_tcp_data(data):
    try:
        data_dict = json.loads(data)
        DeviceData.objects.create(
            device_id=data_dict.get('device_id'),
            location=data_dict.get('location'),
            speed=data_dict.get('speed'),
            # Include other fields as needed
        )
    except Exception as e:
        print(f"Error processing data: {e}")
