# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-07-25 06:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projectManager', '0063_auto_20170724_1824'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServerList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
            ],
        ),
        migrations.AddField(
            model_name='server',
            name='server_list',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='projectManager.ServerList'),
        ),
    ]
