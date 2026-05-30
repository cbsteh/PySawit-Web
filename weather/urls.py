from django.urls import path

from .views import (
    weather_detail,
    weather_list,
    weather_upload,
    weather_download,
    WeatherDelete,
    WeatherUpdate,
    weather_access_nasa,
)

urlpatterns = [
    path('', weather_list, name='weather_list'),
    path('<uuid:slug>/', weather_detail, name='weather_detail'),
    path('<uuid:slug>/delete', WeatherDelete.as_view(), name='weather_delete'),
    path('<uuid:slug>/update', WeatherUpdate.as_view(), name='weather_update'),
    path('<uuid:slug>/download', weather_download, name='weather_download'),
    path('upload/', weather_upload, name='weather_upload'),
    path('ajax/access_nasa/', weather_access_nasa, name='weather_access_nasa'),
]
