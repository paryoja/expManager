# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-07-28 05:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projectManager', '0074_auto_20170727_2028'),
    ]

    operations = [
        migrations.AddField(
            model_name='exptodo',
            name='assigned_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assigned', to='projectManager.Server'),
        ),
    ]