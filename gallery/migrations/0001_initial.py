# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-20 10:18
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import gallery.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('diary', '0017_auto_20170620_1659'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=20, null=True)),
                ('description', models.CharField(blank=True, max_length=80, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DiaryImage',
            fields=[
                ('media_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='gallery.Media')),
                ('img', models.FileField(upload_to=gallery.models.diary_image_upload_to)),
                ('diary', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='diary.Diary')),
            ],
            bases=('gallery.media',),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('media_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='gallery.Media')),
                ('img', models.ImageField(upload_to=gallery.models.image_upload_to)),
                ('user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            bases=('gallery.media',),
        ),
    ]