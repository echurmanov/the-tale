# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-11-05 18:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heroes', '0024_herodescription'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hero',
            name='settings_approved',
        ),
    ]
