# Generated by Django 5.0.4 on 2025-04-12 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField(verbose_name='開始時間')),
                ('class_num', models.IntegerField(default=14)),
                ('id_num', models.IntegerField(default=1)),
                ('name', models.CharField(max_length=255, verbose_name='予約者名')),
            ],
        ),
    ]
