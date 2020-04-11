# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-19 16:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('explorer', '0002_recommendationset_source'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='recommendationset',
            index=models.Index(fields=['page_id', 'source'], name='explorer_re_page_id_1b8332_idx'),
        ),
    ]