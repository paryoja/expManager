# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-12 07:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectManager', '0035_expitem_upload_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='data_info',
            field=models.TextField(null=True),
        ),
    ]