from django.contrib import admin
from .models import City, PackageSize

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'center_latitude', 'center_longitude', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

@admin.register(PackageSize)
class PackageSizeAdmin(admin.ModelAdmin):
    # --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
    list_display = ('name', 'photo', 'is_active') # Заменили 'photo_url' на 'photo'
    # ----------------------
    list_filter = ('is_active',)
    search_fields = ('name',)
