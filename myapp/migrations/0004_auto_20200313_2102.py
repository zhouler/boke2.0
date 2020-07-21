# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_post_post_private'),
    ]

    operations = [
        migrations.AddField(
            model_name='login',
            name='no_talking',
            field=models.BooleanField(verbose_name='是否禁止发言', default=False),
        ),
        migrations.AddField(
            model_name='post',
            name='false_delete',
            field=models.BooleanField(verbose_name='假删除', default=False),
        ),
        migrations.AlterField(
            model_name='post',
            name='post_private',
            field=models.BooleanField(verbose_name='私密文章', default=False),
        ),
    ]
