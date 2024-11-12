from django.db import models

# Create your models here.
class DeviceData(models.Model):
    device_id = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255)
    speed = models.DecimalField(max_digits=10, decimal_places=2)
    # Add other fields as needed

    def __str__(self):
        return f"{self.device_id} at {self.timestamp}"