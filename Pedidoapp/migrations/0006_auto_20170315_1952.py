# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-15 22:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Pedidoapp', '0005_especialidad_estadistica'),
    ]

    operations = [
        migrations.AlterField(
            model_name='especialidad',
            name='estadistica',
            field=models.IntegerField(blank=True, max_length=999),
        ),
    ]
