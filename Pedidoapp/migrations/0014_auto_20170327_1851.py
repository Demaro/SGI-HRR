# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-27 21:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Pedidoapp', '0013_auto_20170327_1821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='especialidad',
            name='acceso',
            field=models.IntegerField(blank=True),
        ),
    ]
