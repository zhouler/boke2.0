# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0010_friendship_unread'),
    ]

    operations = [
        migrations.AlterField(
            model_name='login',
            name='avatar',
            field=models.ImageField(verbose_name='头像', blank=True, default='../media/1.jpg', upload_to=''),
        ),
    ]
