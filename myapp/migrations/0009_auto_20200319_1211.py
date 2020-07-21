# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_friendship_follower_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='readflag',
            field=models.BooleanField(verbose_name='已读', default=False),
        ),
        migrations.AlterField(
            model_name='login',
            name='avatar',
            field=models.ImageField(verbose_name='头像', blank=True, default='1.jpg', upload_to=''),
        ),
    ]
