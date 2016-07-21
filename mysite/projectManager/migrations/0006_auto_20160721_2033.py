# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-21 11:33
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('projectManager', '0005_server'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpTodo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parameters', models.TextField()),
                ('pub_date', models.DateTimeField(verbose_name='date published')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projectManager.Project')),
            ],
        ),
        migrations.AddField(
            model_name='todoitem',
            name='done',
            field=models.BooleanField(default=datetime.datetime(2016, 7, 21, 11, 33, 18, 151200, tzinfo=utc)),
            preserve_default=False,
        ),
    ]