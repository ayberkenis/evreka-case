from django.urls import path
from .views import DeviceDataAPI, DeviceDataListAPI, LatestDeviceDataAPI
from rest_framework.schemas import get_schema_view
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Device Tracking API",
        default_version="v1",
        description="API documentation for device tracking",
        terms_of_service="https://www.evreka.co/",
        contact=openapi.Contact(email="contact@evreka.co"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

urlpatterns = [
    path('data/', DeviceDataAPI.as_view(), name='device_data'),
    path('data/list/', DeviceDataListAPI.as_view(), name='device_data_list'),
    path('data/latest/<str:device_id>/', LatestDeviceDataAPI.as_view(), name='latest_device_data'),
     path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]