"""web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from .views import *
urlpatterns = [


    url(r'^$',index),

    url(r'^content/(\d+)$', content),

    url(r'^base/$',base),

    url(r'^his_homepage/(\d+)/$',his_homepage),

    url(r'^his_homepage/her_post/(\d+)/$',her_post),

    url(r'^his_homepage/her_comment/(\d+)/$',her_comment),

    url(r'^his_homepage/her_fensi/(\d+)/$',her_fensi),

    url(r'^his_homepage/her_guanzhu/(\d+)/$',her_guanzhu),

    url(r'^vip_post/(\d+)/$',vip_post),

    url(r'^vip_post_not/(\d+)/$',vip_post_not),

    url(r'^must_see_blog_posts/$',must_see_blog_posts),

    url(r'^must_see_blog_posts2/$',must_see_blog_posts2),

    url(r'^must_see_blog_posts3/$',must_see_blog_posts3),

    url(r'^message_board/(\d+)/$',message_board),

    url(r'^tags/$',tags),

    url(r'^tags/(\d+)/$',tag_post),

    url(r'mycenter/$',mycenter),#个人中心

    url(r'^send$', send),#ajax发送消息

    url(r'^getting_information$', getting_information),#ajax获取信息

    url(r'^comment$', comment),#评论函数

    url(r'mycenter/my_post/$',my_post),#在我的中心下面的，我的文章

    url(r'mycenter/my_comment/$',my_comment),#在我的中心下面的，我的评论

    url(r'mycenter/my_favorite/$',my_favorite),#在我的中心下面的，我的收藏

    url(r'mycenter/my_friendship/$',my_friendship),#在我的中心下面的，我的关注

    url(r'^mycenter/delete_article/$',delete_article),

    url(r'^mycenter/post_article/$',post_article),

    url(r'^mycenter/post_alter/$',post_alter), # 编辑文章页面

    url(r'^mycenter/post_alter/show_alter_post/', show_alter_post),  # 编辑文章页面，对应显示和修改
    url(r'^simi_post$', simi_post),#ajax修改私密文章
    url(r'^remove_completely_post$', remove_completely_post),  # 彻底删除文章

    url(r'^resume_article$', resume_article),  # 恢复文章

    url(r'^mycenter/account_information/$',account_information),

    url(r'^mycenter/change_password/$',change_password),

    url(r'^mycenter/logout/$',logout),#用户注销账号

    url(r'^mycenter/quit/$',quit),#退出登录

    url(r'^zan$', zan),
    url(r'^cai$', cai),
    url(r'^shoucan$', shoucan),
    url(r'^guanzhu$', guanzhu),
    url(r'^guanzhu2$', guanzhu2),
    url(r'^get_email$', get_email),

    url(r'^delete_article_ajax$', delete_article_ajax),  # 使用ajax批量删除文章


    url(r'^delete_comment$', delete_comment),  # 使用ajax删除评论

    url(r'^delete_message$', delete_message),  # 使用ajax删除留言

    url(r'^sousuo/(\d+)$', sousuo),  # 使用ajax搜索内容


    url(r'register/$',register),#注册

    url(r'login/$',login),#登录

    url(r'forget_password/$',forget_password),#登录忘记密码

    url(r'forget_password_one$', forget_password_one),  # 忘记密码 1

    url(r'forget_password_two$', forget_password_two),  # 忘记密码 2

    url(r'forget_password_three$', forget_password_three),  # 忘记密码 3

    url(r'logout/(\w+)$',logout),##注销


]
