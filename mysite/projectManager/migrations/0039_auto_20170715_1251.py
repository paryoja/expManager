# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-07-15 03:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projectManager', '0038_auto_20170715_1244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datacontainment',
            name='dataset_list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projectManager.DatasetList'),
        ),
    ]
