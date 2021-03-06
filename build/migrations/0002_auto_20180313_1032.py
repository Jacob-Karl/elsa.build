# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-03-13 17:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('build', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataStructure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('structure', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='bundle',
            name='date_coordinates',
        ),
        migrations.RemoveField(
            model_name='bundle',
            name='time_coordinates',
        ),
        migrations.AddField(
            model_name='datastructure',
            name='bundle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='build.Bundle'),
        ),
    ]
