from rest_framework import serializers
from .models import City, PackageSize

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'center_latitude', 'center_longitude', 'is_active']

class PackageSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageSize
        fields = ['id', 'name', 'description', 'photo', 'is_active']
        # 'photo' поле ImageField при сериализации вернет URL к изображению, если настроен MEDIA_URL