# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-20 10:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20170619_1949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=models.ImageField(blank=True, default='', upload_to='avatars/', verbose_name='photo'),
        ),
    ]
