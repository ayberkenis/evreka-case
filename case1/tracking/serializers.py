from rest_framework import serializers
from .models import DeviceData

class DeviceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceData
        fields = '__all__'


class DeviceDataInputSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=255)
    location = serializers.CharField(max_length=255)
    speed = serializers.FloatField()
    timestamp = serializers.DateTimeField(required=False)