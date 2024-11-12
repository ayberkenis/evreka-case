from django.urls import path
from .views import DeviceDataListAPI, LatestDeviceDataAPI

urlpatterns = [
    path('data/list/', DeviceDataListAPI.as_view(), name='tcp_device_data_list'),
    path('data/latest/<str:device_id>/', LatestDeviceDataAPI.as_view(), name='tcp_latest_device_data'),
]