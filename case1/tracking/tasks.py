from celery import shared_task
from .models import DeviceData

@shared_task
def process_device_data(data):
    DeviceData.objects.create(
        device_id=data.get('device_id'),
        location=data.get('location'),
        speed=data.get('speed'),
        # Add other fields as needed
    )
