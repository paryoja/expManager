# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-07-24 09:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projectManager', '0062_datalist_deprecated'),
    ]

    operations = [
        migrations.AddField(
            model_name='exptodo',
            name='algorithm',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='projectManager.Algorithm'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='algorithm',
            name='name',
            field=models.TextField(null=True, verbose_name='Algorithm name'),
        ),
    ]