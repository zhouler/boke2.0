from django.db import models
from .models import *
from DjangoUeditor.models import UEditorField
from django.contrib.auth.models import User
import os
from web import settings
from PIL import Image
from django.db.models.fields.files import ImageFieldFile
import time

#逻辑删除
class MyloginManager(models.Manager): #逻辑删除 重写类 可以在后台中屏蔽 被逻辑删除的对象
    def get_queryset(self):
        # super(PostManage,self).get_queryset() #调用父类的方法
        #  只返回没有被逻辑删除的文章
        return super(MyloginManager,self).get_queryset().filter(is_delete=0)

#每日语句
class Sentence(models.Model):

    time=models.DateTimeField(auto_now=True)
    cotent=models.TextField() #内容,长文本
    def __str__(self):
        return self.cotent
    class Meta:
        verbose_name_plural="每日语句"

#用户表
class Login(models.Model):

    nickname = models.CharField('昵称', max_length=32,blank=True,default="无名")

    avatar = models.ImageField("头像",blank=True,default="../media/1.jpg")  # 图片

    username = models.CharField('用户名',unique=True, max_length=32)  #

    password = models.CharField('密码', max_length=250)  #

    birthday = models.CharField('生日', max_length=32,blank=True)  #生日

    sex = models.CharField('性别',max_length=32,blank=True,default="男")  #性别

    city = models.CharField('所在城市',max_length=32,blank=True)  #城市

    email = models.EmailField('邮箱',blank=True)  #邮箱

    # 建立时间 不能修改
    created_time=models.DateTimeField('建立时间',auto_now_add=True)

    # 修改时间 每次自动更新
    modified_time=models.DateTimeField('修改时间',auto_now=True)


    is_delete=models.BooleanField(default=False,verbose_name='逻辑删除',help_text='逻辑删除')

    if_vip= models.CharField('vip',max_length=32,blank=True,default="非vip")


    no_talking = models.BooleanField('是否禁止发言',blank=True,default=False)

    days_online=models.IntegerField("在线天数",default=1)

    def add_days_online(self):
        self.days_online += 1
        self.save(update_fields=['days_online'])

    def delete(self, using=None,keep_parents=False):
        #重写数据库删除方法 实现逻辑删除
        self.is_delete=True
        self.save()

    class Meta:
        verbose_name_plural = '注册用户'
        ordering = ["-modified_time"]

    def __str__(self):
        return self.nickname

    objects = MyloginManager()#逻辑删除 在后台过滤 被逻辑删除的用户

    def get_follower(self):
        '''
        folloer  关注的人
        :return:
        '''
        user_list = []
        for followed_user in self.nickname.followed.all():
            user_list.append(followed_user.follower)
        return user_list

    def get_followed(self):
        '''
        followed 关注我的人
        :return:
        '''
        user_list = []
        for follower_user in self.nickname.follower.all():
            user_list.append(follower_user.followed)
        return user_list

    def set_follower(self, id):
        '''
        follow some user use id
        :param id:
        :return:
        '''
        try:
            user = User.objects.get(id=id)
        except Exception:
            return None
        # 这是关注的逻辑
        friendship = FriendShip()
        friendship.followed = self.nickname
        friendship.follower = user
        friendship.save()
        return True

# 关注 中间的联系两个user的关系表
class FriendShip(models.Model):
    followed = models.ForeignKey(Login,related_name='followed')
    follower = models.ForeignKey(Login,related_name='follower')

    unread=models.IntegerField("关注对象有多少未读",blank=True,default=0)

    def add_unread(self):
        self.unread += 1
        self.save(update_fields=['unread'])

    follower_pic = models.ImageField("被关注对象图片",blank=True)

    class Meta:
        verbose_name_plural="关注"

#Token表用于登录认证
class Token(models.Model):
    user = models.OneToOneField(to=Login, on_delete=models.CASCADE)
    token = models.CharField('token', max_length=255)
    modified_time = models.DateTimeField('用户登录时间', auto_now=True)

    def __str__(self):
        return self.token
    class Meta:
        verbose_name_plural="认证"

# 标签
class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "标签"

# 文章
class Post(models.Model):
    title = models.CharField("标题", max_length=50)
    author = models.ForeignKey(Login)  # 作者

    choices = (
        ("网站前端", "网站前端"),
        ("后端技术", "后端技术"),
        ("其他", "其他"),
    )
    classfy = models.CharField("分类", max_length=20, choices=choices,blank=True)

    source = models.CharField('来源', max_length=100,blank=True)
    look = models.IntegerField('阅读量', default=0)

    def increase_look(self):
        self.look += 1
        self.save(update_fields=['look'])

    number_of_favorites=models.IntegerField("被收藏的数量",default=0)

    def add_favorites(self):
        self.number_of_favorites += 1
        self.save(update_fields=['number_of_favorites'])

    def del_favorites(self):
        self.number_of_favorites -= 1
        self.save(update_fields=['number_of_favorites'])


    content = UEditorField('内容', width=800, height=600, imagePath="myapp/")

    pub_time = models.DateTimeField("发布时间", auto_now_add=True)
    modify_time = models.DateTimeField('修改时间', auto_now=True)

    zan = models.IntegerField("点赞数", default=0)
    cai = models.IntegerField("脚踩数", default=0)

    tags = models.ManyToManyField(Tag,blank=True)  # 多对多 ,标签

    img = models.ImageField(blank=True)  # 图片
    adv = models.BooleanField("广告位", default=False,blank=True)  # 是否投放到广告位

    vip = models.BooleanField("vip文章", default=False,blank=True)  # 是否设置为vip文章默认否

    post_private = models.BooleanField("私密文章", default=False,blank=True)  # 是否设置为私密文章，默认不是私密文章

    false_delete  = models.BooleanField("回收站", default=False,blank=True)  # 是否设置假删除

    # 缩略图
    thumb = models.ImageField(upload_to="thumb/",blank=True)

    def save(self, raw=False, force_insert=False,
             force_update=False, using=None, update_fields=None):
        super(Post, self).save()
        img_name, ext = os.path.splitext(os.path.basename(self.img.name))
        img_path = os.path.join(settings.MEDIA_ROOT, self.img.name)
        pix = make_thumb(img_path)
        thumb_path = os.path.join(settings.THUMB_DIR, img_name + ".thumb" + ext)
        pix.save(thumb_path)

        self.thumb = ImageFieldFile(self, self.thumb, thumb_path.split(settings.BASE_DIR)[-1])
        super(Post, self).save()

    def author_(self):
        return self.author.username

    author_.short_description = "作者"

    def tag(self):
        return '/'.join([str(i) for i in self.tags.all()])

    tag.short_description = "标签"

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "文章"

#用户收藏
class Favorite(models.Model):

    user = models.ForeignKey(Login)
    picture = models.ForeignKey(Post)
    created_time = models.DateTimeField('关注时间',auto_now_add=True)

    def __unicode__(self):
        return "%s likes picture %s" % (self.user, self.picture)



    class Meta:
        verbose_name_plural="收藏"

#评论表
class Comment(models.Model):

    username=models.ForeignKey(Login)

    content=models.TextField(max_length=1000)

    rand=models.IntegerField(blank=True)

    time=models.DateTimeField(auto_now_add=True)

    #关联文章
    post=models.ForeignKey(Post)


    def post_id(self):
        return self.post
    post_id.short_description="文章"

    class Meta:
        verbose_name_plural="评论表"
        # ordering = ["-time"]  # 按降序排列

#留言
class Message(models.Model):
    username=models.ForeignKey(Login)#作者=外键注册的用户名
    conten=models.CharField(max_length=1000)#内容
    rand=models.IntegerField(blank=True)
    time=models.DateTimeField(auto_now_add=True)#评论时间
    class Meta:
        verbose_name_plural="留言"

def make_thumb(img_path,size=(80,80)):
    img = Image.open(img_path).convert("RGB")
    img.thumbnail(size)
    return img


#邮箱认证
class Email_code(models.Model):
    email=models.CharField(max_length=32)#内容
    code=models.CharField(max_length=12)#内容
    time=models.DateTimeField(auto_now_add=True)#评论时间
    class Meta:
        verbose_name_plural="邮箱认证"

from datetime import datetime, timedelta, tzinfo

class Chat(models.Model):
    author = models.ForeignKey('Login', related_name='Message_Author', null=True, on_delete=models.CASCADE)
    receiver = models.ForeignKey('Login', related_name='Message_Receiver', null=True, on_delete=models.CASCADE)
    content = models.CharField(max_length=500, null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)
    readflag = models.BooleanField("已读", default=False,blank=True)
    remarks = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return ('from %s to %s at %s:%s %s/%s/%s'
                % (self.author, self.receiver, self.time.hour, self.time.minute, self.time.day, self.time.month,
                   self.time.year))