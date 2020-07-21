# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import DjangoUeditor.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('content', models.TextField(max_length=1000)),
                ('rand', models.IntegerField(blank=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': '评论表',
            },
        ),
        migrations.CreateModel(
            name='Email_code',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('email', models.CharField(max_length=32)),
                ('code', models.CharField(max_length=12)),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': '邮箱认证',
            },
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_time', models.DateTimeField(verbose_name='关注时间', auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': '收藏',
            },
        ),
        migrations.CreateModel(
            name='FriendShip',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
            ],
            options={
                'verbose_name_plural': '关注',
            },
        ),
        migrations.CreateModel(
            name='Login',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('nickname', models.CharField(verbose_name='昵称', max_length=32, blank=True, default='无名')),
                ('avatar', models.ImageField(verbose_name='头像', blank=True, upload_to='')),
                ('username', models.CharField(verbose_name='用户名', max_length=32, unique=True)),
                ('password', models.CharField(verbose_name='密码', max_length=250)),
                ('birthday', models.CharField(verbose_name='生日', max_length=32, blank=True)),
                ('sex', models.CharField(verbose_name='性别', max_length=32, blank=True, default='男')),
                ('city', models.CharField(verbose_name='所在城市', max_length=32, blank=True)),
                ('email', models.EmailField(verbose_name='邮箱', max_length=254, blank=True)),
                ('created_time', models.DateTimeField(verbose_name='建立时间', auto_now_add=True)),
                ('modified_time', models.DateTimeField(verbose_name='修改时间', auto_now=True)),
                ('is_delete', models.BooleanField(verbose_name='逻辑删除', default=False, help_text='逻辑删除')),
                ('if_vip', models.CharField(verbose_name='vip', max_length=32, blank=True, default='非vip')),
            ],
            options={
                'verbose_name_plural': '注册用户',
                'ordering': ['-modified_time'],
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('conten', models.CharField(max_length=1000)),
                ('rand', models.IntegerField(blank=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('username', models.ForeignKey(to='myapp.Login')),
            ],
            options={
                'verbose_name_plural': '留言',
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('title', models.CharField(verbose_name='标题', max_length=50)),
                ('classfy', models.CharField(verbose_name='分类', max_length=20, blank=True, choices=[('网站前端', '网站前端'), ('后端技术', '后端技术'), ('其他', '其他')])),
                ('source', models.CharField(verbose_name='来源', max_length=100, blank=True)),
                ('look', models.IntegerField(verbose_name='阅读量', default=0)),
                ('content', DjangoUeditor.models.UEditorField(verbose_name='内容')),
                ('pub_time', models.DateTimeField(verbose_name='发布时间', auto_now_add=True)),
                ('modify_time', models.DateTimeField(verbose_name='修改时间', auto_now=True)),
                ('zan', models.IntegerField(verbose_name='点赞数', default=0)),
                ('cai', models.IntegerField(verbose_name='脚踩数', default=0)),
                ('img', models.ImageField(blank=True, upload_to='')),
                ('adv', models.BooleanField(verbose_name='广告位', default=False)),
                ('vip', models.BooleanField(verbose_name='vip文章', default=False)),
                ('thumb', models.ImageField(blank=True, upload_to='thumb/')),
                ('author', models.ForeignKey(to='myapp.Login')),
            ],
            options={
                'verbose_name_plural': '文章',
            },
        ),
        migrations.CreateModel(
            name='Sentence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('time', models.DateTimeField(auto_now=True)),
                ('cotent', models.TextField()),
            ],
            options={
                'verbose_name_plural': '每日语句',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': '标签',
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('token', models.CharField(verbose_name='token', max_length=255)),
                ('user', models.OneToOneField(to='myapp.Login')),
            ],
            options={
                'verbose_name_plural': '认证',
            },
        ),
        migrations.AddField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(blank=True, to='myapp.Tag'),
        ),
        migrations.AddField(
            model_name='friendship',
            name='followed',
            field=models.ForeignKey(related_name='followed', to='myapp.Login'),
        ),
        migrations.AddField(
            model_name='friendship',
            name='follower',
            field=models.ForeignKey(related_name='follower', to='myapp.Login'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='picture',
            field=models.ForeignKey(to='myapp.Post'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(to='myapp.Login'),
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(to='myapp.Post'),
        ),
        migrations.AddField(
            model_name='comment',
            name='username',
            field=models.ForeignKey(to='myapp.Login'),
        ),
    ]
