from django.urls import path
from .views import DeviceDataAPI, DeviceDataListAPI, LatestDeviceDataAPI

urlpatterns = [
    path('data/', DeviceDataAPI.as_view(), name='device_data'),
    path('data/list/', DeviceDataListAPI.as_view(), name='device_data_list'),
    path('data/latest/<str:device_id>/', LatestDeviceDataAPI.as_view(), name='latest_device_data'),
]