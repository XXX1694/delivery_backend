# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ClientProfile, CourierProfile
from .models import User, ClientProfile, CourierProfile, Car


class ClientProfileInline(admin.StackedInline):  # Или TabularInline для более компактного вида
    model = ClientProfile
    can_delete = False
    verbose_name_plural = 'Профиль клиента'


class CourierProfileInline(admin.StackedInline):
    model = CourierProfile
    can_delete = False
    verbose_name_plural = 'Профиль курьера'


class UserAdmin(BaseUserAdmin):
    # Поля, которые будут отображаться в списке пользователей
    list_display = ('phone_number', 'role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('phone_number',)
    ordering = ('-date_joined',)

    # Убираем стандартные поля username и email из формы редактирования, если они не нужны
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Role', {'fields': ('role',)}),  # Добавляем поле role
    )
    add_fieldsets = (  # Для формы создания нового пользователя
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'role', 'password', 'password2'),  # Добавим password2 для подтверждения
        }),
    )

    # Подключаем инлайны для профилей
    # Важно: инлайны будут отображаться только ПОСЛЕ сохранения основного объекта User
    # и если у User выбрана соответствующая роль (это можно доработать JS в админке)
    inlines = [ClientProfileInline, CourierProfileInline]

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'license_plate', 'created_at')
    search_fields = ('model_name', 'license_plate')

admin.site.register(User, UserAdmin)
admin.site.register(ClientProfile)  # Можно и так, для отдельного управления, но инлайны удобнее
admin.site.register(CourierProfile)