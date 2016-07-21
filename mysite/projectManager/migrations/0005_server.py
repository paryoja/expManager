# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-21 09:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectManager', '0004_auto_20160721_1805'),
    ]

    operations = [
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('server_name', models.CharField(max_length=20)),
                ('server_ip', models.GenericIPAddressField()),
                ('server_cpu', models.CharField(max_length=20, null=True)),
            ],
        ),
    ]