# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-23 02:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectManager', '0002_project_git_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='git_url',
            field=models.TextField(null=True),
        ),
    ]
