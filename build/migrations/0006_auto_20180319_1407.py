# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-03-19 21:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('build', '0005_auto_20180319_1027'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='calibrated',
            name='bundle',
        ),
        migrations.RemoveField(
            model_name='derived',
            name='bundle',
        ),
        migrations.RemoveField(
            model_name='raw',
            name='bundle',
        ),
        migrations.RemoveField(
            model_name='reduced',
            name='bundle',
        ),
        migrations.DeleteModel(
            name='Calibrated',
        ),
        migrations.DeleteModel(
            name='Derived',
        ),
        migrations.DeleteModel(
            name='Raw',
        ),
        migrations.DeleteModel(
            name='Reduced',
        ),
    ]