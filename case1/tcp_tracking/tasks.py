from celery import shared_task
from django.utils import timezone
from .models import DeviceData
import logging
logger = logging.getLogger(__name__)
@shared_task
def process_tcp_data(data_list):
    """
    This function processes a list of device data and stores them in the database.

    Parameters:
    data_list (list): A list of dictionaries, where each dictionary represents a device data.
                      The dictionary should have the following keys: 'device_id', 'location', 'speed', and optionally 'timestamp'.
                      If 'timestamp' is not provided, the current time will be used.

    Returns:
    None

    Raises:
    Exception: If any error occurs during the processing of device data.
    """
    try:

        device_data_instances = [
            DeviceData(
                device_id=data['device_id'],
                location=data['location'],
                speed=data['speed'],
                timestamp=data['timestamp'] if 'timestamp' in data else timezone.now()
            )
            for data in data_list
        ]
        DeviceData.objects.bulk_create(device_data_instances)
        logger.info(f"Successfully processed {len(device_data_instances)} device data.")
    except Exception as e:
        logger.error(f"Error processing device data: {e}")
        raise