# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-24 13:15
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0005_auto_20170918_1431'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='serverstatus',
            managers=[
                ('people', django.db.models.manager.Manager()),
            ],
        ),
    ]
