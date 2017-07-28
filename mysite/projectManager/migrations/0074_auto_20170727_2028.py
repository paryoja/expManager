# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-07-27 11:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projectManager', '0073_algorithm_execute_script'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exptodo',
            name='server',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='projectManager.Server'),
        ),
        migrations.AlterField(
            model_name='exptodo',
            name='serverlist',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='projectManager.ServerList'),
        ),
    ]