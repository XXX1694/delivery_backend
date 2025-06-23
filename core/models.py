import os
from django.db import models
from django.utils.text import slugify
from django.utils.crypto import get_random_string

# --- Функция для загрузки фото Размера Заказа ---
def get_package_size_upload_path(instance, filename):
    """
    Генерирует путь для загрузки фото размера заказа.
    """
    name_slug = slugify(instance.name)
    ext = filename.split('.')[-1].lower()
    random_chars = get_random_string(6)
    new_filename = f"{name_slug}_{random_chars}.{ext}"
    return os.path.join('package_sizes', name_slug, new_filename)

class City(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название города')
    center_latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Широта центра'
    )
    center_longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Долгота центра'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        ordering = ['name']

class PackageSize(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название размера')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    photo = models.ImageField(
        upload_to=get_package_size_upload_path, 
        blank=True, null=True, verbose_name='Фото размера'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Размер заказа'
        verbose_name_plural = 'Размеры заказов'
        ordering = ['name']