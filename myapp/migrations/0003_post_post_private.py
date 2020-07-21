# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_post_number_of_favorites'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='post_private',
            field=models.BooleanField(verbose_name='私密文章', default=True),
        ),
    ]
