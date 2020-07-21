# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_auto_20200319_1211'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendship',
            name='unread',
            field=models.IntegerField(verbose_name='关注对象有多少未读', blank=True, default=0),
        ),
    ]
