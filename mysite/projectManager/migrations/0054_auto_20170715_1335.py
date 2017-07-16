# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-07-15 04:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projectManager', '0053_auto_20170715_1329'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', models.TextField(null=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projectManager.Project')),
            ],
        ),
        migrations.RemoveField(
            model_name='datasetlist',
            name='project',
        ),
        migrations.AlterField(
            model_name='datacontainment',
            name='data_list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projectManager.DataList'),
        ),
        migrations.DeleteModel(
            name='DataSetList',
        ),
    ]
