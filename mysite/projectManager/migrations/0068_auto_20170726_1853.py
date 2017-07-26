# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-07-26 09:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projectManager', '0067_auto_20170725_2210'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exptodo',
            name='datalist',
        ),
        migrations.AddField(
            model_name='exptodo',
            name='dataset',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='projectManager.Dataset'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='exptodo',
            name='query',
            field=models.TextField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='exptodo',
            name='server',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='projectManager.Server'),
        ),
        migrations.AlterField(
            model_name='exptodo',
            name='serverlist',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='projectManager.ServerList'),
        ),
    ]
