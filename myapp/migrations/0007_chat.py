# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_login_days_online'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('content', models.CharField(max_length=500, blank=True, null=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('readflag', models.CharField(max_length=6, default='UNREAD')),
                ('remarks', models.CharField(max_length=500, blank=True, null=True)),
                ('author', models.ForeignKey(null=True, related_name='Message_Author', to='myapp.Login')),
                ('receiver', models.ForeignKey(null=True, related_name='Message_Receiver', to='myapp.Login')),
            ],
        ),
    ]
