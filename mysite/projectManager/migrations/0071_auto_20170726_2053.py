# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-07-26 11:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectManager', '0070_auto_20170726_1942'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='initialize_code',
            field=models.FileField(null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='project',
            name='project_setting_file',
            field=models.FileField(null=True, upload_to=''),
        ),
    ]
