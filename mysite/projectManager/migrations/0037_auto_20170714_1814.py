# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-07-14 09:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projectManager', '0036_dataset_data_info'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataContainment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projectManager.Dataset')),
            ],
        ),
        migrations.CreateModel(
            name='DataSetList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', models.TextField(null=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projectManager.Project')),
            ],
        ),
        migrations.AddField(
            model_name='datacontainment',
            name='dataset_list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projectManager.DataSetList'),
        ),
    ]
