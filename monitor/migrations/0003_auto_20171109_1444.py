# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-09 06:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0002_graph'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='graph',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='zabbixhost',
            options={'ordering': ['ip']},
        ),
    ]