from django.urls import path
from .views import CityListAPIView, PackageSizeListAPIView

app_name = 'core_api'

urlpatterns = [
    path('cities/', CityListAPIView.as_view(), name='city_list'),
    path('packagesizes/', PackageSizeListAPIView.as_view(), name='packagesize_list'),
]