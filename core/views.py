from rest_framework import generics, permissions
from .models import City, PackageSize
from .serializers import CitySerializer, PackageSizeSerializer

class CityListAPIView(generics.ListAPIView):
    queryset = City.objects.filter(is_active=True) # Показываем только активные города
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny] # Список городов доступен всем

class PackageSizeListAPIView(generics.ListAPIView):
    queryset = PackageSize.objects.filter(is_active=True) # Только активные размеры
    serializer_class = PackageSizeSerializer
    permission_classes = [permissions.AllowAny] # Список размеров доступен всем