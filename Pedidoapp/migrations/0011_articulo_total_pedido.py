# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-20 11:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Pedidoapp', '0010_especialidad_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='articulo',
            name='total_pedido',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
