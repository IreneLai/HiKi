# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-04 13:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diary',
            name='content',
            field=models.CharField(max_length=1000),
        ),
    ]
