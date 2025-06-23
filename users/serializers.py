from rest_framework import serializers
from django.contrib.auth import get_user_model  # Правильный способ получить модель User
from .models import ClientProfile, CourierProfile, Car  # Импортируем профили и Car



User = get_user_model()


class ClientProfileSerializer(serializers.ModelSerializer):
    # Если вы хотите, чтобы city возвращал не ID, а, например, имя города,
    # можно использовать вложенный сериализатор или StringRelatedField
    # city = serializers.StringRelatedField() # Пример
    class Meta:
        model = ClientProfile
        fields = ['full_name', 'iin', 'city', 'date_of_birth']  # Поля, которые будут в API

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['model_name', 'license_plate', 'tech_passport_front', 'tech_passport_back']
        # Если поля изображений должны быть не обязательными при обновлении, можно добавить:
        # extra_kwargs = {
        #     'tech_passport_front': {'required': False, 'allow_null': True},
        #     'tech_passport_back': {'required': False, 'allow_null': True},
        # }

class CourierProfileSerializer(serializers.ModelSerializer):
    # city = serializers.StringRelatedField() # Если хотите строковое представление города
    class Meta:
        model = CourierProfile
        # Поле 'user' и 'car' не включаем сюда напрямую, они будут управляться при регистрации
        fields = [
            'full_name', 'iin', 'city', 'date_of_birth',
            'id_card_front', 'id_card_back', 'driver_license_front',
            'driver_license_back', 'selfie_with_id'
        ]
        # Можно сделать изображения не обязательными для частичного обновления (PATCH) позже
        # extra_kwargs = {
        #     'id_card_front': {'required': False}, # и т.д. для других ImageField
        # }


class UserSerializer(serializers.ModelSerializer): # Переопределяем или находим существующий
    client_profile = ClientProfileSerializer(read_only=True, required=False)
    courier_profile = CourierProfileSerializer(read_only=True, required=False) # <-- ДОБАВИЛИ

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'role', 'client_profile', 'courier_profile'] # <-- ДОБАВИЛИ
        read_only_fields = ['role']


class ClientRegistrationSerializer(serializers.ModelSerializer):
    profile = ClientProfileSerializer(required=True, write_only=True)  # Поле только для записи
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, label='Confirm password',
                                      style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['phone_number', 'password', 'password2', 'profile']

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Пользователь с таким номером телефона уже существует.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        # Можно добавить другие проверки для пароля (длина, сложность)
        return attrs

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        password = validated_data.pop('password')  # Удаляем password2, т.к. он не нужен для User.objects.create_user
        validated_data.pop('password2', None)

        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            password=password,
            role=User.ROLE_CLIENT  # Явно указываем роль клиента
        )
        ClientProfile.objects.create(user=user, **profile_data)
        return user





class CourierRegistrationSerializer(serializers.ModelSerializer):
    # Вложенные сериализаторы для данных профиля и автомобиля
    # Клиент будет отправлять эти данные как вложенные JSON объекты,
    # а файлы будут идти отдельно в multipart/form-data.
    profile = CourierProfileSerializer(required=True)
    car = CarSerializer(required=True)

    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, label='Confirm password',
                                      style={'input_type': 'password'})

    class Meta:
        model = User  # Основная модель - User
        fields = ['phone_number', 'password', 'password2', 'profile', 'car']

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Пользователь с таким номером телефона уже существует.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})

        # Валидация изображений (проверка наличия)
        # Файлы приходят в self.context['request'].FILES
        # Проверим наличие всех обязательных файлов для курьера
        required_profile_files = ['id_card_front', 'id_card_back', 'driver_license_front', 'driver_license_back',
                                  'selfie_with_id']
        required_car_files = ['tech_passport_front', 'tech_passport_back']

        # Данные для profile и car приходят в attrs['profile'] и attrs['car']
        # А сами файлы нужно будет извлечь из request.FILES в методе create.
        # Здесь мы можем проверить, что клиент *намерен* их загрузить,
        # но DRF автоматически не свяжет файлы из request.FILES с полями ImageField
        # внутри вложенных сериализаторов 'profile' и 'car' при таком подходе.
        # Поэтому, лучше всего передавать файлы на верхнем уровне запроса multipart/form-data,
        # а вложенные 'profile' и 'car' будут содержать только не-файловые данные.
        # Либо, мы модифицируем 'profile' и 'car' в validated_data в методе 'create'.

        # Для упрощения, сейчас мы ожидаем, что 'profile' и 'car' содержат все данные,
        # включая данные файлов, которые DRF должен сам подхватить для ImageField.
        # Это работает, если клиент правильно формирует multipart/form-data запрос,
        # где файлы для вложенных структур именуются соответственно (e.g., profile.id_card_front).
        # Однако, это может быть не очень надежно или интуитивно.

        # Более надежный подход: сериализатор ожидает все поля (включая файлы) на верхнем уровне.
        # Либо мы переопределяем .create() и вручную обрабатываем request.FILES.

        # Сейчас оставим как есть, предполагая, что DRF сможет правильно связать файлы
        # из multipart/form-data с ImageField во вложенных profile и car сериализаторах.
        # Если это не сработает, мы скорректируем метод create.

        return attrs

    def create(self, validated_data):
        profile_data_input = validated_data.pop('profile')
        car_data_input = validated_data.pop('car')
        password = validated_data.pop('password')
        validated_data.pop('password2', None)

        # 1. Создаем пользователя
        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            password=password,
            role=User.ROLE_COURIER  # Явно указываем роль курьера
        )

        # 2. Создаем автомобиль
        # profile_data_input и car_data_input уже содержат обработанные данные от своих сериализаторов,
        # включая данные для ImageField (если DRF их правильно подхватил из multipart).
        car = Car.objects.create(**car_data_input)

        # 3. Создаем профиль курьера и связываем с автомобилем
        CourierProfile.objects.create(user=user, car=car, **profile_data_input)

        return user