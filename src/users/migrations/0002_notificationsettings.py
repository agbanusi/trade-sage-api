# Generated by Django 5.1.7 on 2025-04-18 00:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signal_notifications', models.BooleanField(default=True)),
                ('email_notifications', models.BooleanField(default=True)),
                ('push_notifications', models.BooleanField(default=True)),
                ('sound_alerts', models.BooleanField(default=True)),
                ('signal_alerts', models.BooleanField(default=True)),
                ('price_alerts', models.BooleanField(default=True)),
                ('pattern_recognition', models.BooleanField(default=True)),
                ('economic_news_alerts', models.BooleanField(default=False)),
                ('max_signals_per_day', models.IntegerField(default=15)),
                ('signal_quality_filter', models.CharField(choices=[('high', 'High quality signals only (70%+ confidence)'), ('medium', 'Medium and high quality (50%+ confidence)'), ('all', 'All signals')], default='high', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='notification_settings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
