# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_auto_20200314_1114'),
    ]

    operations = [
        migrations.AddField(
            model_name='login',
            name='days_online',
            field=models.IntegerField(verbose_name='在线天数', default=1),
        ),
    ]
