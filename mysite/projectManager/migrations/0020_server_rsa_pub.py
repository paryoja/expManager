# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-11 17:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectManager', '0019_expitem_invalid'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='rsa_pub',
            field=models.CharField(max_length=200, null=True),
        ),
    ]