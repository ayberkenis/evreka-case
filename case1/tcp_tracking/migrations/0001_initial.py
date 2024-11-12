# Generated by Django 5.1.3 on 2024-11-12 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_id', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('location', models.CharField(max_length=255)),
                ('speed', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
    ]
