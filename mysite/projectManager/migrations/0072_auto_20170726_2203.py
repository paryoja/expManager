# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-07-26 13:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectManager', '0071_auto_20170726_2053'),
    ]

    operations = [
        migrations.AddField(
            model_name='exptodo',
            name='is_finished',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='exptodo',
            name='is_running',
            field=models.BooleanField(default=False),
        ),
    ]
