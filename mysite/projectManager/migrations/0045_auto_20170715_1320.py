# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-07-15 04:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projectManager', '0044_auto_20170715_1316'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datacontainment',
            name='dataset',
        ),
        migrations.RemoveField(
            model_name='datacontainment',
            name='dataset_list',
        ),
        migrations.DeleteModel(
            name='DataContainment',
        ),
    ]