# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_chat'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendship',
            name='follower_pic',
            field=models.ImageField(verbose_name='被关注对象图片', blank=True, upload_to=''),
        ),
    ]
