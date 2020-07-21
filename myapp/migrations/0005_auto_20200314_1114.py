# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_auto_20200313_2102'),
    ]

    operations = [
        migrations.AddField(
            model_name='token',
            name='modified_time',
            field=models.DateTimeField(verbose_name='用户登录时间', default=datetime.datetime(2020, 3, 14, 11, 14, 38, 945819), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='post',
            name='false_delete',
            field=models.BooleanField(verbose_name='回收站', default=False),
        ),
    ]
