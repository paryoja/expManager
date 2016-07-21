# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-21 09:05
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('projectManager', '0003_expitem_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='todoitem',
            name='deadline_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 7, 21, 9, 5, 37, 207413, tzinfo=utc), verbose_name=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='todoitem',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 7, 21, 9, 5, 57, 846900, tzinfo=utc), verbose_name='date published'),
            preserve_default=False,
        ),
    ]
