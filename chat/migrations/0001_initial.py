# Generated by Django 5.2.1 on 2025-06-23 14:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Время последнего сообщения')),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='chat_session', to='orders.order', verbose_name='Заказ')),
            ],
            options={
                'verbose_name': 'Чат сессия',
                'verbose_name_plural': 'Чат сессии',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_content', models.TextField(verbose_name='Текст сообщения')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Время отправки')),
                ('is_read', models.BooleanField(default=False, verbose_name='Прочитано')),
                ('sender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sent_chat_messages', to=settings.AUTH_USER_MODEL, verbose_name='Отправитель')),
                ('chat_session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.chatsession', verbose_name='Чат сессия')),
            ],
            options={
                'verbose_name': 'Сообщение в чате',
                'verbose_name_plural': 'Сообщения в чатах',
                'ordering': ['timestamp'],
            },
        ),
    ]
