from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Sentence)
admin.site.register(Tag)


@admin.register(Login)
class Postlogin(admin.ModelAdmin):
    list_display = ('username','nickname','password','created_time','modified_time')#在 处展示

    search_fields = ['username']  # 添加搜索字段 按类别 category__categoty_name
    # ist_filter = ['title','category'] # 过滤器
    list_per_page = 10  # 一页三条数据

@admin.register(Message)
class Message(admin.ModelAdmin):
    list_display = ('time','username','conten')#在 处展示

    list_per_page = 10  # 一页三条数据

@admin.register(FriendShip)
class FriendShip(admin.ModelAdmin):
    list_display = ('followed','follower','follower_pic','unread')#在 处展示
    list_per_page = 10  # 一页三条数据


# @admin.register(UserPermission)
# class UserPermission(admin.ModelAdmin):
#     list_display = ('user','user_type')#在 处展示
#     list_per_page = 10  # 一页三条数据


@admin.register(Favorite)
class Favorite(admin.ModelAdmin):
    list_display = ('user','picture','created_time')#在 处展示
    list_per_page = 10  # 一页三条数据


@admin.register(Token)
class Token(admin.ModelAdmin):
    list_display = ('user', 'token','modified_time')  # 在 处展示
    list_per_page = 10  # 一页三条数据

@admin.register(Comment)
class c(admin.ModelAdmin):
    list_display = ['username','content','time','post_id']

@admin.register(Chat)
class Chat_(admin.ModelAdmin):
    list_display = ['author','receiver','content','time','readflag']


class p(admin.ModelAdmin):
    list_display = ['title','author','classfy','pub_time',
                    'zan','cai','look','source','tag','adv','vip',"number_of_favorites"]
    # fields = ['title','content','teated_time','tag']
    fieldsets = (
         ('标题/正文',{'fields':['title','content']}),#author 是昵称，author_账号
         ('分类/图片',{'fields':['classfy','img']}),
         ('作者',{'fields':['author']}),
         ('标签',{'fields':['tags']}),
         ('来源',{'fields':['source']}),
         ('广告位',{'fields':['adv']}),
         ('vip',{'fields':['vip']}),
         ('私密文章',{'fields':['post_private']}),
         ('回收站',{'fields':['false_delete']}),


    )

    list_filter = ['title','classfy']
    list_per_page = 15

class p_line(admin.TabularInline):
    model = Post
    extra = 15
admin.site.register(Post,p)


