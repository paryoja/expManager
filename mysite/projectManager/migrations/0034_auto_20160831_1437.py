# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-31 05:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectManager', '0033_auto_20160831_1411'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='git_url',
            field=models.TextField(blank=True, null=True),
        ),
    ]
