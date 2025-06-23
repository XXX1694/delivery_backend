# users/models.py
import uuid
import os
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from core.models import City # Импортируем модель City из приложения core


# --- ОСНОВНЫЕ ФУНКЦИИ ДЛЯ ГЕНЕРАЦИИ ПУТЕЙ ---
def get_courier_document_upload_path(instance, filename, doc_type_readable):
    """
    Генерирует путь для загрузки документа курьера с именем файла, включающим ИИН и тип документа.
    'instance' - экземпляр CourierProfile.
    'filename' - оригинальное имя файла.
    'doc_type_readable' - читаемое название типа документа (например, "Уд личн лицевая").
    """
    iin = instance.iin
    ext = filename.split('.')[-1].lower()  # Получаем расширение файла в нижнем регистре
    doc_type_slug = slugify(doc_type_readable)
    random_chars = get_random_string(6)
    new_filename = f"{iin}_{doc_type_slug}_{random_chars}.{ext}"
    return os.path.join('couriers', str(instance.user.id), doc_type_slug, new_filename)


def get_car_document_upload_path(instance, filename, doc_type_readable):
    """
    Генерирует путь для загрузки документа автомобиля.
    'instance' - экземпляр Car.
    'doc_type_readable' - читаемое название типа документа.
    """
    license_plate_slug = slugify(instance.license_plate)  # Используем номер машины
    ext = filename.split('.')[-1].lower()
    doc_type_slug = slugify(doc_type_readable)
    random_chars = get_random_string(6)
    new_filename = f"{license_plate_slug}_{doc_type_slug}_{random_chars}.{ext}"
    car_identifier_folder = str(instance.id) if instance.id else license_plate_slug
    return os.path.join('cars', car_identifier_folder, doc_type_slug, new_filename)


# --- ФУНКЦИИ-ОБЕРТКИ ДЛЯ COURIERPROFILE UPLOAD_TO ---
def courier_id_card_front_path(instance, filename):
    return get_courier_document_upload_path(instance, filename, 'id-card-front')


def courier_id_card_back_path(instance, filename):
    return get_courier_document_upload_path(instance, filename, 'id-card-back')


def courier_driver_license_front_path(instance, filename):
    return get_courier_document_upload_path(instance, filename, 'driver-license-front')


def courier_driver_license_back_path(instance, filename):
    return get_courier_document_upload_path(instance, filename, 'driver-license-back')


def courier_selfie_with_id_path(instance, filename):
    return get_courier_document_upload_path(instance, filename, 'selfie-with-id')


# --- ФУНКЦИИ-ОБЕРТКИ ДЛЯ CAR UPLOAD_TO ---
def car_tech_passport_front_path(instance, filename):
    return get_car_document_upload_path(instance, filename, 'tech-passport-front')


def car_tech_passport_back_path(instance, filename):
    return get_car_document_upload_path(instance, filename, 'tech-passport-back')


# --- Менеджер для кастомной модели User ---
class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)  # Хеширует пароль
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)


# --- Кастомная модель User ---
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CLIENT = 'client'
    ROLE_COURIER = 'courier'
    ROLE_CHOICES = [
        (ROLE_CLIENT, 'Клиент'),
        (ROLE_COURIER, 'Курьер'),
    ]

    phone_number = models.CharField(max_length=20, unique=True, verbose_name='Номер телефона')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name='Роль')

    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_staff = models.BooleanField(default=False, verbose_name='Сотрудник')
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='Дата регистрации')

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone_number

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


# --- Профиль Клиента ---
class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='client_profile')
    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    iin = models.CharField(max_length=12, verbose_name='ИИН', unique=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Город')
    date_of_birth = models.DateField(verbose_name='Дата рождения')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Клиент: {self.full_name} ({self.user.phone_number})"

    class Meta:
        verbose_name = 'Профиль Клиента'
        verbose_name_plural = 'Профили Клиентов'


# --- Модель Автомобиля ---
class Car(models.Model):
    model_name = models.CharField(max_length=100, verbose_name='Название модели')
    license_plate = models.CharField(max_length=20, unique=True, verbose_name='Номер машины')
    tech_passport_front = models.ImageField(
        upload_to=car_tech_passport_front_path,
        verbose_name='Техпаспорт (лицевая)'
    )
    tech_passport_back = models.ImageField(
        upload_to=car_tech_passport_back_path,
        verbose_name='Техпаспорт (обратная)'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.model_name} ({self.license_plate})"

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'


# --- Профиль Курьера ---
class CourierProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='courier_profile')
    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    iin = models.CharField(max_length=12, verbose_name='ИИН', unique=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Город')
    date_of_birth = models.DateField(verbose_name='Дата рождения')

    id_card_front = models.ImageField(
        upload_to=courier_id_card_front_path,
        verbose_name='Уд. личности (лицевая)'
    )
    id_card_back = models.ImageField(
        upload_to=courier_id_card_back_path,
        verbose_name='Уд. личности (обратная)'
    )
    driver_license_front = models.ImageField(
        upload_to=courier_driver_license_front_path,
        verbose_name='Вод. удостоверение (лицевая)'
    )
    driver_license_back = models.ImageField(
        upload_to=courier_driver_license_back_path,
        verbose_name='Вод. удостоверение (обратная)'
    )
    selfie_with_id = models.ImageField(
        upload_to=courier_selfie_with_id_path,
        verbose_name='Селфи с уд. личности'
    )

    car = models.OneToOneField(Car, on_delete=models.SET_NULL, null=True, blank=True,
                               verbose_name='Автомобиль')  # Ссылка на Car

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Курьер: {self.full_name} ({self.user.phone_number})"

    class Meta:
        verbose_name = 'Профиль Курьера'
        verbose_name_plural = 'Профили Курьеров'