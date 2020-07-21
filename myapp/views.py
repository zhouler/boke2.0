import json
import uuid
from django.contrib.auth.hashers import make_password,check_password
from django.shortcuts import render, render_to_response
from django.http import HttpResponse,JsonResponse
from .models import *
from django.utils import timezone
from django.core.paginator import Paginator
import datetime
import time
import random
from django.shortcuts import render,get_object_or_404
from django.views.generic import ListView

from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Q
"""认证函数"""
"""返回值1：登录 ，-1：未登录 """
def renzheng(request):
    try:
        token=request.session['token']
    except:
        return -1 # 您还没有登录

    if not token:
        return -1 # 您还没有登录
    user_token_object = Token.objects.filter(token=token).first()
    if not user_token_object:
        return -1 # 您还没有登录
    return 1

"""注册用户函数"""
def register(request):
    if request.method=="GET":
        return render(request,"register.html")

    elif request.method=="POST":

        user_info = request.POST
        username = user_info.get("username")
        password1 = user_info.get("password1")
        password2 = user_info.get("password2")
        input_email = user_info.get("input_email")
        email = user_info.get("email")

        try:
            e=Email_code.objects.filter(email=email).order_by("-time").first()
            if str(input_email) != str(e.code):
                return render(request, 'register.html', context={"flog": 3})  # flog=2 验证码校验失败
        except Exception:
            return render(request, 'register.html', context={"flog": 3})
        L = Login.objects.filter(is_delete=0, username=username).first()
        if  L:
            return render(request, 'register.html', context={"flog": 2})# 用户已经存在
        if password1!=password2:
            return render(request, 'register.html', context={"flog": 1})#两次密码不一致！

        t=Login()#实例化
        t.username=username #增加新的字段
        password1=make_password(password1)
        t.password=password1 #增加新的字段
        t.email=email #增加新的字段
        t.save()#保存
        return redirect("/login")

"""登录函数"""
def login(request):

    if request.method=="GET":

        return render(request,"login_user.html")

    elif request.method=="POST":

        user_info = request.POST
        username = user_info.get("username")

        password = user_info.get("password")

        L = Login.objects.filter(is_delete=0,username=username).first()

        if not L:
            return render(request, 'login_user.html', context={"flog": 1})  # 返回登录页面，显示账号错误

        ret=check_password(password,L.password)#解码

        if ret:
            try:
                now_time = datetime.datetime.now().strftime("%Y-%m-%d")
                token_obj = Token.objects.filter(user=L).first()
                time_token = token_obj.modified_time.strftime("%Y-%m-%d")
                list1 = []  # 保存当前时间
                list2 = []  # 保存用户上次登录时间
                for i, j in zip(now_time.split("-"), time_token.split("-")):
                    list1.append(i)
                    list2.append(j)

                if int(list1[2]) > int(list2[2]):
                    Login.add_days_online(L)
                elif int(list1[1]) > int(list2[1]):
                    Login.add_days_online(L)
                elif int(list1[0]) > int(list2[0]):
                    Login.add_days_online(L)

            except Exception:
                pass



            token = str(uuid.uuid4())#生成随机的字符串token
            request.session['token'] = token
            request.session['username'] = username
            try:
                request.session['nickrname'] = L.nickname#如果能获取到，说明用户不是第一次登录
            except:
                request.session['nickrname'] = None
            Token.objects.update_or_create(user=L, defaults={'token': token})

            return redirect("../")

        return render(request, 'login_user.html', context={"flog": 2})  # 返回登录页面，显示密码错误

"""忘记密码函数"""
def forget_password(request):

    return render(request,"forget_password.html")

"""个人中心函数"""
def mycenter(request):
    ret=renzheng(request)
    if ret==-1:
        return HttpResponse("未登录")
    username=request.session.get("username")

    uer_obj=Login.objects.filter(username=username).first()

    uer_post=len(Post.objects.filter(post_private=False).filter(false_delete=False).filter(author=uer_obj))#获该用户的所有发布的文章

    user_momment=len(Comment.objects.filter(username=uer_obj))#获该用户的所有评论

    user_message=len(Message.objects.filter(username=uer_obj))#获该用户的所有评论

    user_favorite=len(Favorite.objects.filter(user=uer_obj))#获该用户的所有收藏

    user_friendship=len(FriendShip.objects.filter(followed=uer_obj))#获该用户的所有关注个数


    user_obj_friendship=FriendShip.objects.filter(followed=uer_obj)#获取关注的人

    list1=[]
    for i in user_obj_friendship:
        list1.append(i.follower)

    list=Chat.objects.filter(receiver=uer_obj)

    list2=[]
    for i in  list:
        if i.author in list1:
            pass
        else:
            list2.append(i)


    list4=[]#该用户没有关注的用户，但是有发了信息给他
    from itertools import chain


    for i in list2:
        n=Login.objects.filter(id=i.author_id)
        list4.append(n)


    try:
        for i in range(len(list4)):

                if i>len(list4)-2:

                    break
                ret=list4[i + 1] = chain(list4[i],list4[i+1])

    except BaseException:
        ret=None
    if (len(list4))==0:
        ret=None

    formatList = []#对陌生人消息去重
    try:
        for id in ret:
            if id not in formatList:
                formatList.append(id)
    except:
        pass

    if  request.is_ajax():
        id = request.POST.get("id")
        followed_id=Login.objects.filter(username=request.session.get("username")).first()

        char_user = Chat.objects.filter(Q(author_id=id) | Q(receiver_id=id)).order_by("time")
        FriendShip.objects.filter(followed=followed_id.id,follower=id).update(unread=0)

        for i in char_user:
            Chat.objects.filter(id=i.id).update(readflag=True)
        data_list = []
        # 将评论数据构造成列表
        for com in char_user:
            dic = {}
            dic["author"] = com.author.id #发送方id
            dic["receiver"] = com.receiver.id #接收方id

            dic["id"] = id #你查看的用户聊天窗口

            dic["pic"] = str(Login.objects.filter(id=id).first().avatar)


            dic["username"] = str(uer_obj.username)
            dic["time"] = com.time.strftime('%Y-%m-%d %H:%M:%S')  # 格式化时间
            dic["content"] = com.content
            data_list.append(dic)


        return JsonResponse({"data": data_list})



    return render(request,'personal_center.html',context={"uer_post":uer_post,
      "user_momment":user_momment,"user_favorite":user_favorite,
      "user_friendship":user_friendship,"uer_obj":uer_obj,
      "user_message":user_message,"user_obj_friendship":user_obj_friendship,
      "list4":formatList})




"""我的文章函数"""
def my_post(request):
    ret=renzheng(request)
    if ret==-1:
        return HttpResponse("未登录")
    username=request.session.get("username")

    uer_obj=Login.objects.filter(username=username).first()

    uer_post=(Post.objects.filter(post_private=False).filter(false_delete=False).filter(author=uer_obj))#获该用户的所有发布的文章
    try:
        ran = random.randint(0, len(Sentence.objects.all()) - 1)  # 随机获取一条
    except:
        ran=None
    sentence = Sentence.objects.all()[ran]  # 每日一句
    sentence.time = timezone.now()

    p1 = Post.objects.filter(post_private=False).filter(false_delete=False).values('author').distinct().count()  # 统计作者
    p2 = Post.objects.filter(post_private=False).filter(false_delete=False).all().count()  # 统计文章
    p3 = Comment.objects.count()  # 统计评论
    p4 = Message.objects.all().count()  # 统计留言

    comment = Comment.objects.order_by('-time')[:5]
    now_time = datetime.datetime.now()
    # 当前天 显示当前日期是本周第几天
    day_num = now_time.isoweekday()
    # 计算当前日期所在周一
    week_day = (now_time - datetime.timedelta(days=day_num))

    username = request.session.get("username")
    username = Login.objects.filter(username=username).first()

    post_zan = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by(
        '-zan')[
               :5]  # 点赞文章
    post_fav = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by(
        '-number_of_favorites')[:5]  # 本周最多收藏



    return render(request,'my_post.html',context={"post1":uer_post,"s": sentence,
        "c": comment, "p1": p1, "p2": p2,"p3": p3, "p4": p4,"username":username,
        "post_zan":post_zan ,"post_fav":post_fav,
                                                  })

"""我的评论函数"""
def my_comment(request):
    ret=renzheng(request)
    if ret==-1:
        return HttpResponse("未登录")
    username=request.session.get("username")

    uer_obj=Login.objects.filter(username=username)

    user_momment=(Comment.objects.filter(username=uer_obj))#获该用户的所有评论

    user_message=(Message.objects.filter(username=uer_obj))#获该用户的所有留言
    try:
        ran = random.randint(0, len(Sentence.objects.all()) - 1)  # 随机获取一条
    except:
        ran=None

    sentence = Sentence.objects.all()[ran]  # 每日一句
    sentence.time = timezone.now()

    p1 = Post.objects.filter(post_private=False).filter(false_delete=False).values('author').distinct().count()  # 统计作者
    p2 = Post.objects.filter(post_private=False).filter(false_delete=False).all().count()  # 统计文章
    p3 = Comment.objects.count()  # 统计评论
    p4 = Message.objects.all().count()  # 统计留言

    comment = Comment.objects.order_by('-time')[:5]
    now_time = datetime.datetime.now()
    # 当前天 显示当前日期是本周第几天
    day_num = now_time.isoweekday()
    # 计算当前日期所在周一
    week_day = (now_time - datetime.timedelta(days=day_num))

    username = request.session.get("username")
    username = Login.objects.filter(username=username).first()

    post_zan = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by(
        '-zan')[
               :5]  # 点赞文章
    post_fav = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by(
        '-number_of_favorites')[:5]  # 本周最多收藏

    return render(request,'my_comment.html',context={"user_momment":user_momment,
    "user_message":user_message,"s": sentence, "c": comment, "p1": p1, "p2": p2,
         "p3": p3, "p4": p4,"username":username,"post_zan":post_zan
         ,"post_fav":post_fav


                                                     })

"""我的收藏函数"""
def my_favorite(request):
    ret=renzheng(request)
    if ret==-1:
        return HttpResponse("未登录")
    username=request.session.get("username")

    uer_obj=Login.objects.filter(username=username)

    user_favorite = (Favorite.objects.filter(user=uer_obj))  # 获该用户的所有收藏
    try:
        ran = random.randint(0, len(Sentence.objects.all()) - 1)  # 随机获取一条
    except:
        ran=None
    sentence = Sentence.objects.all()[ran]  # 每日一句
    sentence.time = timezone.now()

    p1 = Post.objects.filter(post_private=False).filter(false_delete=False).values('author').distinct().count()  # 统计作者
    p2 = Post.objects.filter(post_private=False).filter(false_delete=False).all().count()  # 统计文章
    p3 = Comment.objects.count()  # 统计评论
    p4 = Message.objects.all().count()  # 统计留言

    comment = Comment.objects.order_by('-time')[:5]
    now_time = datetime.datetime.now()
    # 当前天 显示当前日期是本周第几天
    day_num = now_time.isoweekday()
    # 计算当前日期所在周一
    week_day = (now_time - datetime.timedelta(days=day_num))

    username = request.session.get("username")
    username = Login.objects.filter(username=username).first()

    post_zan = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by(
        '-zan')[
               :5]  # 点赞文章
    post_fav = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by(
        '-number_of_favorites')[:5]  # 本周最多收藏

    list=[]
    for i in user_favorite:
        p = Post.objects.filter(post_private=False).filter(false_delete=False).filter(id=i.picture_id).first()
        list.append(p)
    return render(request,'my_favorite.html',context={"user_favorite":list,
          "s": sentence, "c": comment, "p1": p1, "p2": p2,
          "p3": p3, "p4": p4, "username": username, "post_zan": post_zan
        , "post_fav": post_fav
            })

"""我的关注"""
def my_friendship(request):
    ret=renzheng(request)
    if ret==-1:
        return HttpResponse("未登录")
    username=request.session.get("username")

    uer_obj=Login.objects.filter(username=username)

    user_friendship=(FriendShip.objects.filter(followed=uer_obj))#获该用户的所有关注

    list=[]
    for i in user_friendship:
        p = Login.objects.filter(id=i.follower_id).first()
        list.append(p)
    try:
        ran = random.randint(0, len(Sentence.objects.all()) - 1)  # 随机获取一条
    except:
        ran=None

    sentence = Sentence.objects.all()[ran]  # 每日一句
    sentence.time = timezone.now()

    p1 = Post.objects.filter(post_private=False).filter(false_delete=False).values('author').distinct().count()  # 统计作者
    p2 = Post.objects.filter(post_private=False).filter(false_delete=False).all().count()  # 统计文章
    p3 = Comment.objects.count()  # 统计评论
    p4 = Message.objects.all().count()  # 统计留言

    comment = Comment.objects.order_by('-time')[:5]
    now_time = datetime.datetime.now()
    # 当前天 显示当前日期是本周第几天
    day_num = now_time.isoweekday()
    # 计算当前日期所在周一
    week_day = (now_time - datetime.timedelta(days=day_num))

    username = request.session.get("username")
    username = Login.objects.filter(username=username).first()

    post_zan = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by(
        '-zan')[
               :5]  # 点赞文章
    post_fav = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by(
        '-number_of_favorites')[:5]  # 本周最多收藏

    return render(request,'my_friendship.html',context={"user_friendship":list,
            "s": sentence, "c": comment, "p1": p1, "p2": p2,
            "p3": p3, "p4": p4, "username": username, "post_zan": post_zan
            , "post_fav": post_fav
                                                        })

"""发布文章函数"""
def post_article(request):

    ret=renzheng(request)
    if ret==-1:
        return HttpResponse("未登录")
    username=request.session.get("username")
    if request.method=="GET":

        uer_obj = Login.objects.filter(username=username).first()
        tag=Tag.objects.all()
        return render(request, 'post_article.html',context={"uer_obj":uer_obj,"tag":tag})

    elif request.method=="POST":

        title = request.POST.get("title")#标题
        img_file = request.FILES.get("file")#文章图片

        classification = request.POST.get("classification")
        t = request.POST.get("t")#标签

        list = []
        for i in t.split(","):
            if i != "":
                list.append((Tag.objects.filter(name=i).first()))
        source = request.POST.get("source")#来源
        vip = request.POST.get("vip")#获取是否为vip文章
        content = request.POST.get("data")#获取文章内容

        username = request.session['username']
        usr_obj=Login.objects.filter(username=username).first()#获取用户对象

        # 发布文章的数据保存
        try:
            p=Post()#实例化
            p.title=title
            p.author=usr_obj
            p.classfy=classification
            p.source=source
            p.content=content
            p.vip=int(vip)
            p.img=img_file
            p.save()
            for i in  list:
                p.tags.add(i)
        except Exception:
            return HttpResponse("发布失败")

        return HttpResponse("发布成功")

"""修改文章函数"""
def post_alter(request):

    ret=renzheng(request)
    if ret==-1:
        return HttpResponse("未登录")
    username=request.session.get("username")
    if request.method=="GET":

        uer_obj = Login.objects.filter(username=username).first()
        tag=Tag.objects.all()
        p=Post.objects.filter(post_private=False).filter(false_delete=False).filter(author=uer_obj)

        p_gongkai=Post.objects.filter(author=uer_obj).filter(post_private=False).filter(false_delete=False)

        p_quanbu=Post.objects.filter(author=uer_obj).all()

        p_private=Post.objects.filter(author=uer_obj).filter(post_private=True)

        p_false_delete=Post.objects.filter(author=uer_obj).filter(false_delete=True)


        return render(request, 'post_alter.html',context=
        {"uer_obj":uer_obj,"p":p,"tag":tag,"p_gongkai":p_gongkai,
        "p_private":p_private,"p_false_delete":p_false_delete,
        "p_quanbu":p_quanbu
                                                          })

    if request.method == "POST":


        title = request.POST.get("title")  # 标题
        img_file = request.FILES.get("file")  # 文章图片

        classification = request.POST.get("classification")
        t = request.POST.get("t")  # 标签

        list = []
        for i in t.split(","):
            if i != "":
                list.append((Tag.objects.filter(name=i).first()))
        source = request.POST.get("source")  # 来源
        vip = request.POST.get("vip")  # 获取是否为vip文章
        content = request.POST.get("data")  # 获取文章内容

        username = request.session['username']
        usr_obj = Login.objects.filter(username=username).first()  # 获取用户对象

        # 发布文章的数据保存
        try:
            p = Post()  # 实例化
            p.title = title
            p.author = usr_obj
            p.classfy = classification
            p.source = source
            p.content = content
            p.vip = int(vip)
            p.img = img_file
            p.save()
            for i in list:
                p.tags.add(i)
        except Exception:
            return HttpResponse("发布失败")

        return HttpResponse("发布成功")

    elif request.method=="POST":

        title = request.POST.get("title")#标题
        img_file = request.FILES.get("file")#文章图片

        classification = request.POST.get("classification")
        t = request.POST.get("t")#标签

        list = []
        for i in t.split(","):
            if i != "":
                list.append((Tag.objects.filter(name=i).first()))
        source = request.POST.get("source")#来源
        vip = request.POST.get("vip")#获取是否为vip文章
        content = request.POST.get("data")#获取文章内容

        username = request.session['username']
        usr_obj=Login.objects.filter(username=username).first()#获取用户对象

        # 发布文章的数据保存
        try:
            p=Post()#实例化
            p.title=title
            p.author=usr_obj
            p.classfy=classification
            p.source=source
            p.content=content
            p.vip=int(vip)
            p.img=img_file
            p.save()
            for i in  list:
                p.tags.add(i)
        except Exception:
            return HttpResponse("发布失败")

        return HttpResponse("发布成功")

"""删除页面文章函数"""
def delete_article(request):

    ret=renzheng(request)
    if ret==-1:
        return HttpResponse("未登录")
    username=request.session.get("username")

    u=Login.objects.filter(username=username).first()
    uer_obj=Post.objects.filter(post_private=False).filter(false_delete=False).filter(author=u).filter(false_delete=False)

    return render(request,'Delete_article.html',context={'uer_obj': uer_obj,"len":len(uer_obj)})


"""ajax批量删除文章"""
def delete_article_ajax(request):
    del_post_id = request.POST.get("arr")
    list=[]
    for i in  del_post_id.split(","):
        if i!="":
            list.append(int(i))
    try:
        for i in list:
            Post.objects.filter(post_private=False).filter(false_delete=False).filter(id=i).update(false_delete=True)
    except:
        return HttpResponse("删除失败")
    return HttpResponse("删除成功")

"""博文彻底删除"""
def remove_completely_post(request):

    del_post_id = request.POST.get("id")
    try:
        Post.objects.filter(post_private=False).filter(false_delete=False).filter(id=del_post_id).delete()
    except:
        return HttpResponse(2)
    return HttpResponse(1)

"""博文恢复"""
def resume_article(request):
    del_post_id = request.POST.get("id")
    try:
        Post.objects.filter(id=del_post_id).update(false_delete=False)
    except:
        return HttpResponse(2)
    return HttpResponse(1)

"""ajax批量删除评论"""
def delete_comment(request):
    comment_id = request.POST.get("id")
    try:
        Comment.objects.filter(id=comment_id).delete()
    except:
        return HttpResponse("删除失败")

    return HttpResponse(comment_id)


"""ajax批量删除留言"""
def delete_message(request):

    message_id = request.POST.get("id")
    try:
        Message.objects.filter(id=message_id).delete()
    except:
        return HttpResponse("删除失败")

    return HttpResponse(message_id)


"""显示对应文章文章"""
def show_alter_post(request):

    if request.method == "GET":
        post_id = request.GET.get("post_id")
        p=Post.objects.filter(id=post_id).first()

        user=request.session.get("username")
        uer_obj=Login.objects.filter(username=user).first()
        tag=Tag.objects.all()
        return render(request,"show_alter_post.html",
                context={"p":p,"tag":tag,"uer_obj":uer_obj})
    if request.method == "POST":
        post_id = request.POST.get("id")
        title = request.POST.get("title")  # 标题
        img_file = request.FILES.get("file")  # 文章图片

        classification = request.POST.get("classification")
        t = request.POST.get("t")  # 标签

        list = []
        for i in t.split(","):
            if i != "":
                list.append((Tag.objects.filter(name=i).first()))
        source = request.POST.get("source")  # 来源
        vip = request.POST.get("vip")  # 获取是否为vip文章
        content = request.POST.get("data")  # 获取文章内容

        username = request.session['username']
        usr_obj = Login.objects.filter(username=username).first()  # 获取用户对象

        # 发布文章的数据保存


        Post.objects.filter(post_private=False).filter(false_delete=False).update_or_create(id=post_id, defaults=
        {'title': title,"author":usr_obj,"classfy":classification,
         "source":source,"content":content,"vip":(vip)
         })
        if img_file:
            Post.objects.filter(post_private=False).filter(false_delete=False).update_or_create(id=post_id, defaults=
            {"img":img_file
             })

        return HttpResponse("修改成功")


"""账户信息函数"""
def account_information(request):

    ret=renzheng(request)
    if ret==-1:
        return HttpResponse("未登录")
    username=request.session.get("username")
    if request.method=="GET":

        uer_obj = Login.objects.filter(username=username).first()

        return render(request, 'account_information.html', context={"uer_obj": uer_obj})

    elif request.method=="POST":


        try:
            username = request.session['username']
            user_info = request.POST
            nickname = user_info.get("nickname")
            birthday = user_info.get("birthday")
            sex = user_info.get("sex")
            email = user_info.get("email")
            city = user_info.get("city")
            file = request.FILES.get("file")  # 获取头像图片
            Login.objects.filter(username=username).update_or_create(defaults={"nickname":nickname,
                                            "birthday":birthday,"sex":sex,"email":email,"city":city,"avatar":file})
            if  file:
                Login.objects.filter(username=username).update(avatar=file)

        except Exception:
            return HttpResponse("保存失败")
        return HttpResponse("保存成功")

"""账户更改密码"""
def change_password(request):

    ret=renzheng(request)
    if ret==-1:
        return HttpResponse("未登录")
    username=request.session.get("username")
    if request.method=="GET":

        uer_obj = Login.objects.filter(username=username).first()

        return render(request, 'change_password.html', context={"uer_obj": uer_obj})

    elif request.method=="POST":
        username = request.session['username']
        user_obj=Login.objects.filter(username=username).first()
        user_info = request.POST
        old_password = user_info.get("old_password")
        new_password = user_info.get("new_password")
        agin_password = user_info.get("agin_password")

        if new_password!=agin_password:
            return HttpResponse("输入的两次密码不一致")
        ret = check_password(old_password, user_obj.password)# 解密

        if ret==0:
            return HttpResponse("密码错误")

        password = make_password(agin_password)#密码进行加密

        Login.objects.filter(username=username).update(password=password)

        return HttpResponse("密码更改成功，请牢记，打死也不告诉别人！")

"""账户注销"""
def logout(request):
    ret=renzheng(request)
    if ret==-1:
        return HttpResponse("未登录")
    username=request.session.get("username")
    if request.method == "GET":

        uer_obj = Login.objects.filter(username=username).first()

        return render(request, 'logout.html', context={"uer_obj": uer_obj})

    elif request.method == "POST":

        user_password = request.POST
        password1 = user_password.get("password1")
        password2 = user_password.get("password2")
        if password1!=password2:
            return HttpResponse("两次密码不一致")

        username = request.session['username']
        token = request.session['token']

        uer_obj=Login.objects.filter(username=username).first()
        ret = check_password(password1, uer_obj.password)  # 解码
        if ret==0:
            return HttpResponse("密码不正确")

        u = Login.objects.filter(username=username)
        if len(u) > 0:
            u[0].is_delete = True
            u[0].save()
            Token.objects.filter(token=token).delete()#清除token，退出用户登录
            return HttpResponse("注销成功")
        else:
            return HttpResponse("用户不存在")



"""退出登录函数"""
def quit(request):
    try:
        del request.session['username']
        del request.session['token']
    except:
        return HttpResponse("退出登录失败")
    else:
        return HttpResponse("退出登录成功")

"""ajax更新被踩"""
def cai(request):
    try:
        id_=request.POST.get("id")
        p=Post.objects.filter(post_private=False).filter(false_delete=False).get(pk=id_)
    except BaseException as e:
        return HttpResponse(e)
    else:
        id_cai=request.session.get(id_+"cai",False)
        if not id_cai or time.time() >id_cai:#如果没有获取到时间戳 或者时间搓还有过期
            p.cai+=1
            p.save()
            request.session[id_+"cai"]=time.time()+60*60*24 #点赞后24小时之后才能再次点


    return HttpResponse(p.cai)

"""ajax更新点赞"""
def zan(request):
    try:
        id_=request.POST.get("id")
        p=Post.objects.filter(post_private=False).filter(false_delete=False).get(pk=id_)
    except BaseException as e:
        return HttpResponse(e)
    else:
        id_zan=request.session.get(id_+"zan",False)
        if not id_zan or time.time() >id_zan:#如果没有获取到时间戳 或者时间搓还有过期
            p.zan+=1
            p.save()
            request.session[id_+"zan"]=time.time()+60*60*24 #点赞后 24小时之后才能再次点


    return HttpResponse(p.zan)

"""ajax更新收藏"""
def shoucan(request):
    ret=renzheng(request)
    if ret==-1:
        return HttpResponse("未登录")
    username=request.session.get("username")

    try:

        id_=request.POST.get("id")
        p=Post.objects.filter(post_private=False).filter(false_delete=False).get(pk=id_)#生成post对象
        user_obj = Login.objects.filter(username=username).first()
    except BaseException as e:
        return HttpResponse(e)
    else:
        ret=Favorite.objects.filter(user=user_obj).filter(picture=p).first()

        if ret:
            Favorite.objects.filter(user=user_obj, picture=p).delete()
            Post.del_favorites(p)
            return HttpResponse("已取")

        else:#如果没有就创建
            Favorite.objects.create(user=user_obj,picture=p)
            Post.add_favorites(p)
            return HttpResponse("已收")


"""ajax更新关注"""
def guanzhu(request):
    ret=renzheng(request)
    if ret==-1:
        return HttpResponse("未登录")
    username=request.session.get("username")
    try:
        id_=request.POST.get("id")
        p=Post.objects.filter(post_private=False).filter(false_delete=False).filter(pk=id_).first()#生成post对象
        user_obj = Login.objects.filter(username=username).first()#关注人 对象
        favo_obj = Login.objects.filter(nickname=p.author).first()#被关注人 对象
    except BaseException as e:
        return HttpResponse(e)
    else:
        if user_obj==favo_obj:
            return HttpResponse("不能")

        ret=FriendShip.objects.filter(followed=user_obj).filter(follower=favo_obj).first()

        if ret:#已经关注
            FriendShip.objects.filter(followed=user_obj, follower=favo_obj).delete()
            return HttpResponse("已取")
        else:
            FriendShip.objects.create(followed=user_obj, follower=favo_obj,follower_pic=favo_obj.avatar)
            return HttpResponse("已关")

"""他的主页关注"""
def guanzhu2(request):
    ret=renzheng(request)
    if ret==-1:
        return HttpResponse("未登录")
    username=request.session.get("username")
    try:

        id_=request.POST.get("id")

        user_obj = Login.objects.filter(username=username).first()#关注人 对象
        favo_obj = Login.objects.filter(id=id_).first()#被关注人 对象
    except BaseException as e:
        return HttpResponse(e)
    else:
        if user_obj==favo_obj:
            return HttpResponse("不能")

        ret=FriendShip.objects.filter(followed=user_obj).filter(follower=favo_obj).first()

        if ret:#已经关注
            FriendShip.objects.filter(followed=user_obj, follower=favo_obj).delete()
            return HttpResponse("已取")
        else:
            FriendShip.objects.create(followed=user_obj, follower=favo_obj,follower_pic=favo_obj.avatar)
            return HttpResponse("已关")

"""ajax发送email"""
def get_email(request):
    email=request.POST.get("email")
    print(email)
    email=str(email)
    rand4=str(random.randint(1000, 9999))
    from django.core.mail import send_mail
    from web import settings

    try:
        html_message = "验证码：{}".format(rand4)

        send_mail('个人博客用户注册邮箱验证码','个人博客',settings.EMAIL_FROM,
                  ['{}'.format(email)],html_message=html_message,fail_silently=False
                  )
    except Exception:
        return render(request, 'register.html', context={"flog": 3})
    else:
        Email_code.objects.create(email=email,code=rand4)

"""ajax修改私密文章"""
def simi_post(request):
    id=request.POST.get("id")

    post_obj=Post.objects.filter(id=id).first()
    if post_obj.post_private==1:
        Post.objects.filter(id=id).update(post_private=0)
        return HttpResponse(2)
    else:
        Post.objects.filter(id=id).update(post_private=1)
        return HttpResponse(1)

"""博文详情页"""
def content(request,f):
    username=request.session.get("username")
    username=Login.objects.filter(username=username).first()
    p = Post.objects.filter(post_private=False).filter(false_delete=False).filter(id=f)[0]  # 获得对应文章

    if username.if_vip=="非vip" and p.vip==1:
        return HttpResponse("您不是vip用户，不能查看vip文章")


    try:
        ran = random.randint(0, len(Sentence.objects.all()) - 1)  # 随机获取一条
    except:
        ran=None
    sentence = Sentence.objects.all()[ran]  # 每日一句
    sentence.time = timezone.now()

    from django.db.models import Q
    hot_post = Post.objects.filter(post_private=False).filter(false_delete=False).filter(author=p.author).filter(~Q(id=p.id)).order_by('-look')[:6]  # 该作者的热门文章

    p1 = Post.objects.filter(post_private=False).filter(false_delete=False).values('author').distinct().count()  # 统计作者
    p2 = Post.objects.filter(post_private=False).filter(false_delete=False).all().count()  # 统计文章
    p3 = Comment.objects.count()  # 统计评论
    p4 = Message.objects.all().count()  # 统计留言

    now_time = datetime.datetime.now()
    # 当前天 显示当前日期是本周第几天
    day_num = now_time.isoweekday()
    # 计算当前日期所在周一
    week_day = (now_time - datetime.timedelta(days=day_num))
    post_zan = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by('-zan')[:5]#点赞文章

    post_fav = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by('-number_of_favorites')[:5]#本周最多收藏

    comment = Comment.objects.order_by('-time')[:5]  # 最新评论

    try:
        left = random.randint(0, len(Post.objects.filter(classfy=p.classfy)) - 1)  # 猜你喜欢
        right = random.randint(0, len(Post.objects.filter(classfy=p.classfy)) + 1)  # 猜你喜欢
        left = Post.objects.all()[left]
        right = Post.objects.all()[right]
    except:
        left=None
        right = None

    Post.increase_look(p)  # 获得阅读量

    user_obj = Login.objects.filter(id=p.author_id)


    return render(request, 'content.html',
      context={'post': hot_post, "s": sentence, "c": comment,
               "p1": p1, "p2": p2, "p3": p3, "p4": p4,
               "p": p, "user_obj": user_obj, "left": left,
               "right": right,"post_zan":post_zan,
               "post_fav":post_fav,"username":username})


"""评论函数"""
def comment(request):
    ret=renzheng(request)
    if ret==-1:
        return HttpResponse("未登录")

    username=request.session.get("username")
    user_obj = Login.objects.filter(username=username).first()

    if user_obj.no_talking == True:
        return HttpResponse("您已经被禁言，请联系管理员****@qq.com")

    commentContent = request.POST.get("commentContent")

    commentID = request.POST.get("commentID")#文章的id

    try:
        # 保存评论内容
        comment = Comment()

        L=Login.objects.filter(username=username).first()
        comment.username = L
        comment.content = commentContent
        comment.time = time.time()
        comment.post_id = commentID
        comment.rand = random.randint(1,30)
        comment.save()

    except :
        return HttpResponse("数据库保存失败")

    finally:

        # 先获取到评论的文章
        detail_comment = Comment.objects.filter(post=commentID).order_by("-time")[:100]
        data_list = []
        # 将评论数据构造成列表
        for com in detail_comment:
            dic = {}
            dic["name"] = str(com.username)
            dic["time"] = com.time.strftime('%Y-%m-%d')  # 格式化时间
            dic["content"] = com.content
            dic["random"] = random.randint(1,30)
            data_list.append(dic)

        return JsonResponse({"data": data_list})

"""主页函数"""
def index(request):
    now_time = datetime.datetime.now()
    # 当前天 显示当前日期是本周第几天
    day_num = now_time.isoweekday()
    # 计算当前日期所在周一
    week_day = (now_time - datetime.timedelta(days=day_num))

    post_week = Post.objects.filter(post_private=False).filter(false_delete=False).order_by('-pub_time')[:5]

    try:
        ran = random.randint(0, len(Sentence.objects.all()) - 1)  # 随机获取一条
    except:
        ran=None

    sentence = Sentence.objects.all()[ran]  # 每日一句
    sentence.time = timezone.now()
    adv = Post.objects.filter(post_private=False).filter(false_delete=False).filter(adv=True)

    post = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by('-look')[:5]#热门文章

    post_zan = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by('-zan')[:5]#点赞文章

    post_fav = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by('-number_of_favorites')[:5]#本周最多收藏


    p1 = Post.objects.filter(post_private=False).filter(false_delete=False).values('author').distinct().count()  # 统计作者
    p2 = Post.objects.filter(post_private=False).filter(false_delete=False).all().count()  # 统计文章
    p3 = Comment.objects.count()  # 统计评论
    p4 = Message.objects.all().count()  # 统计留言

    comment = Comment.objects.order_by('-time')[:5]# 最新评论

    username=request.session.get("username")
    username=Login.objects.filter(username=username).first()

    try:

        now_time = datetime.datetime.now().strftime("%Y-%m-%d")
        token_obj = Token.objects.filter(user=username).first()
        time_token = token_obj.modified_time.strftime("%Y-%m-%d")
        list1 = []  # 保存当前时间
        list2 = []  # 保存用户上次登录时间
        for i, j in zip(now_time.split("-"), time_token.split("-")):
            list1.append(i)
            list2.append(j)

        if int(list1[2]) > int(list2[2]):

            Login.add_days_online(username)
            Token.objects.filter(user_id=username.id).update(modified_time=datetime.datetime.now())
        elif int(list1[1]) > int(list2[1]):

            Login.add_days_online(username)
        elif int(list1[0]) > int(list2[0]):

            Login.add_days_online(username)

    except Exception:

        pass

    if request.method =='GET':

        return render(request, 'index.html',
                      context={'post': post, "s": sentence, "c": comment,
                               "p1": p1, "p2": p2, "p3": p3, "p4": p4,
                               "adv": adv, "post_week": post_week,
                               "post_zan":post_zan,"post_fav":post_fav,
                               "username":username})

"""搜索函数"""
def sousuo(request,pindex):

    user_info = request.POST
    sousuo = user_info.get("sousuo")
    name = Login.objects.filter(nickname=sousuo).first()
    if name==None:
        post1=Post.objects.filter(post_private=False).filter(false_delete=False).filter(title=sousuo)
    else:
        post1 = Post.objects.filter(post_private=False).filter(false_delete=False).filter(Q(title=sousuo) | Q(author_id=name.id))

    paginator = Paginator(post1, 3)
    if pindex == "":  # django中默认返回空值，所以加以判断，并设置默认值为1
        pindex = 1
    else:  # 如果有返回在值，把返回值转为整数型
        int(pindex)
    page = paginator.page(pindex)

    now_time = datetime.datetime.now()
    # 当前天 显示当前日期是本周第几天
    day_num = now_time.isoweekday()
    # 计算当前日期所在周一
    week_day = (now_time - datetime.timedelta(days=day_num))

    # 查询一周内的数据
    post_week = Post.objects.filter(post_private=False).filter(false_delete=False).order_by('-pub_time')[:5]

    try:
        ran = random.randint(0, len(Sentence.objects.all()) - 1)  # 随机获取一条
    except:
        ran=None
    sentence = Sentence.objects.all()[ran]  # 每日一句
    sentence.time = timezone.now()
    adv = Post.objects.filter(post_private=False).filter(false_delete=False).filter(adv=True)

    post = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by('-look')[:5]  # 热门文章

    post_zan = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by('-zan')[:5]  # 点赞文章

    p1 = Post.objects.filter(post_private=False).filter(false_delete=False).values('author').distinct().count()  # 统计作者
    p2 = Post.objects.filter(post_private=False).filter(false_delete=False).all().count()  # 统计文章
    p3 = Comment.objects.count()  # 统计评论
    p4 = Message.objects.all().count()  # 统计留言

    comment = Comment.objects.order_by('-time')[:5]  # 最新评论
    return render(request, 'seach.html',
                  context={"post1": post1,'post': post, "s": sentence, "c": comment, "p1": p1, "p2": p2, "p3": p3, "p4": p4,
                           "adv": adv, "post_week": post_week,"post_zan":post_zan,"page":page})

"""留言板函数"""
def message_board(request,pindex):

    m = Message.objects.order_by("-time")
    paginator = Paginator(m, 25)
    if pindex == "":  # django中默认返回空值，所以加以判断，并设置默认值为1
        pindex = 1
    else:  # 如果有返回在值，把返回值转为整数型
        int(pindex)
    page = paginator.page(pindex)


    sentence = Sentence.objects.first()
    sentence.time = timezone.now()
    post = Post.objects.filter(post_private=False).filter(false_delete=False).order_by('-look')[:5]

    p1 = Post.objects.filter(post_private=False).filter(false_delete=False).values('author').distinct().count()  # 统计作者
    p2 = Post.objects.filter(post_private=False).filter(false_delete=False).all().count()  # 统计文章
    p3 = Comment.objects.count()  # 统计评论
    p4 = Message.objects.all().count()  # 统计留言

    comment1 = Comment.objects.order_by('-time')[:5]
    now_time = datetime.datetime.now()
    # 当前天 显示当前日期是本周第几天
    day_num = now_time.isoweekday()
    # 计算当前日期所在周一
    week_day = (now_time - datetime.timedelta(days=day_num))

    username = request.session.get("username")
    username = Login.objects.filter(username=username).first()

    post_zan = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by('-zan')[
               :5]  # 点赞文章
    post_fav = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by(
        '-number_of_favorites')[:5]  # 本周最多收藏

    if request.method=="GET":

        return render(request, 'message_board.html',
                context={'post': post, "s": sentence, "c": comment1,
                "p1": p1, "p2": p2, "p3": p3, "p4": p4,"m": m,
                "page":page,"username":username,"post_zan":post_zan,
                "post_fav":post_fav
                         })


    elif request.method=="POST":
        ret = renzheng(request)
        if ret == -1:
            return HttpResponse("未登录")
        username = request.session.get("username")

        user_obj = Login.objects.filter(username=username).first()

        if user_obj.no_talking==True:
            return HttpResponse("您已经被禁言,请联系管理员****@qq.com")


        commentContent = request.POST.get("commentContent")

        user = Login.objects.filter(username=username).first()

        try:
            # 保存留言内容
            comment = Message()
            comment.username = user
            comment.conten = commentContent
            comment.time = time.time()
            comment.rand = random.randint(1,30)
            comment.save()

        except Exception as e:
            return HttpResponse("留言失败")

        finally:
            data_list = Message.objects.order_by("-time")[:100]
            paginator = Paginator(data_list, 25)

            if pindex == "":  # django中默认返回空值，所以加以判断，并设置默认值为1
                pindex = 1
            else:  # 如果有返回在值，把返回值转为整数型
                int(pindex)
            page = paginator.page(pindex)

            return render(request, 'message_board.html',
                          context={'post': post, "s": sentence, "c": comment1, "p1": p1, "p2": p2, "p3": p3, "p4": p4,
                                   "m": m,"data": data_list,"page":page})


"""标签页函数"""
def tags(request):
    if request.method=="GET":

        try:
            ran = random.randint(0, len(Sentence.objects.all()) - 1)  # 随机获取一条
        except:
            ran = None
        sentence = Sentence.objects.all()[ran]  # 每日一句
        sentence.time = timezone.now()

        p1 = Post.objects.filter(post_private=False).filter(false_delete=False).values('author').distinct().count()  # 统计作者
        p2 = Post.objects.filter(post_private=False).filter(false_delete=False).all().count()  # 统计文章
        p3 = Comment.objects.count()  # 统计评论
        p4 = Message.objects.all().count()  # 统计留言

        comment = Comment.objects.order_by('-time')[:5]
        now_time = datetime.datetime.now()
        # 当前天 显示当前日期是本周第几天
        day_num = now_time.isoweekday()
        # 计算当前日期所在周一
        week_day = (now_time - datetime.timedelta(days=day_num))

        username = request.session.get("username")
        username = Login.objects.filter(username=username).first()

        post_zan = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by(
            '-zan')[
                   :5]  # 点赞文章
        post_fav = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by(
            '-number_of_favorites')[:5]  # 本周最多收藏

        t = Tag.objects.all()
        return render(request, "tags.html", context={"t": t,
         "s": sentence, "c": comment, "p1": p1, "p2": p2,
         "p3": p3, "p4": p4,"username":username,"post_zan":post_zan
         ,"post_fav":post_fav
                                                     })

    elif request.method=="POST":
        ret = renzheng(request)

        if ret == -1:
            return HttpResponse("未登录")

        tag = request.POST.get("tag")

        if len(tag)==0:
            return HttpResponse("内容不能为空")

        if Tag.objects.filter(name=tag).first():
            return HttpResponse("标签已经存在")
        else:
            Tag.objects.create(name=tag)
            return HttpResponse("新建标签成功！")

"""查看同类标签函数"""
def tag_post(request,pindex):
    t1 = Tag.objects.filter(id=pindex).first()#找到这个类型的 tag对象
    p = Post.objects.filter(post_private=False).filter(false_delete=False).filter(tags=t1)
    return render(request, "tags_post.html", context={"page": p,"t1":t1})

"""动态模板函数"""
def base(request):

    sentence=Sentence.objects.first()
    sentence.time=timezone.now()

    post = Post.objects.filter(post_private=False).filter(false_delete=False).order_by('-look')[:5]

    p1 = Post.objects.filter(post_private=False).filter(false_delete=False).values('author').distinct() .count()#统计作者
    p2 = Post.objects.filter(post_private=False).filter(false_delete=False).all().count()#统计文章
    p3= Comment.objects.count()#统计评论
    p4 = Message.objects.all().count()#统计留言

    comment = Comment.objects.order_by('-time')[:5]


    return render(request,'base1.html',context={'post': post,"s":sentence,"c":comment,"p1":p1,"p2":p2,"p3":p3,"p4":p4})

"""vip模板函数"""
def vip_post(request, pindex):
    ret=renzheng(request)
    if ret==-1:
        return HttpResponse("未登录")
    username=request.session.get("username")

    L=Login.objects.filter(username=username).first()

    if L.if_vip=="非vip":
        return HttpResponse("您不是vip用户查看不了该内容，请联系邮箱：******@qq.com")

    vip_post=Post.objects.filter(post_private=False).filter(false_delete=False).filter(vip=1)
    paginator = Paginator(vip_post, 5)
    if pindex == "":  # django中默认返回空值，所以加以判断，并设置默认值为1
        pindex = 1
    else:  # 如果有返回在值，把返回值转为整数型
        int(pindex)
    page = paginator.page(pindex)

    sentence = Sentence.objects.first()
    sentence.time = timezone.now()

    post = Post.objects.filter(post_private=False).filter(false_delete=False).order_by('-look')[:5]

    p1 = Post.objects.filter(post_private=False).filter(false_delete=False).values('author').distinct().count()  # 统计作者
    p2 = Post.objects.filter(post_private=False).filter(false_delete=False).all().count()  # 统计文章
    p3 = Comment.objects.count()  # 统计评论
    p4 = Message.objects.all().count()  # 统计留言

    comment = Comment.objects.order_by('-time')[:5]
    username=request.session.get("username")
    username=Login.objects.filter(username=username).first()

    now_time = datetime.datetime.now()
    # 当前天 显示当前日期是本周第几天
    day_num = now_time.isoweekday()
    # 计算当前日期所在周一
    week_day = (now_time - datetime.timedelta(days=day_num))
    post_zan = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by('-zan')[:5]  # 点赞文章
    post_fav = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by('-number_of_favorites')[:5]  # 本周最多收藏

    return render(request,'vip_post.html',context={
        "post1":vip_post,'post': post,"s":sentence,"c":comment,
        "p1":p1,"p2":p2,"p3":p3,"p4":p4,"page":page,
        "username":username,"post_zan":post_zan,"post_fav":post_fav
    })

"""非vip模板函数"""
def vip_post_not(request, pindex):

    vip_post=Post.objects.filter(post_private=False).filter(false_delete=False).filter(vip=0)
    paginator = Paginator(vip_post, 5)

    if pindex == "":  # django中默认返回空值，所以加以判断，并设置默认值为1
        pindex = 1
    else:  # 如果有返回在值，把返回值转为整数型
        int(pindex)
    page = paginator.page(pindex)


    sentence = Sentence.objects.first()
    sentence.time = timezone.now()

    post = Post.objects.filter(post_private=False).filter(false_delete=False).order_by('-look')[:5]

    p1 = Post.objects.filter(post_private=False).filter(false_delete=False).values('author').distinct().count()  # 统计作者
    p2 = Post.objects.filter(post_private=False).filter(false_delete=False).all().count()  # 统计文章
    p3 = Comment.objects.count()  # 统计评论
    p4 = Message.objects.all().count()  # 统计留言

    comment = Comment.objects.order_by('-time')[:5]

    now_time = datetime.datetime.now()
    # 当前天 显示当前日期是本周第几天
    day_num = now_time.isoweekday()
    # 计算当前日期所在周一
    week_day = (now_time - datetime.timedelta(days=day_num))

    username=request.session.get("username")
    username=Login.objects.filter(username=username).first()

    post_zan = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by('-zan')[
               :5]  # 点赞文章
    post_fav = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by(
        '-number_of_favorites')[:5]  # 本周最多收藏

    return render(request,'vip_post_not.html',context={
        "post1":vip_post,'post': post,"s":sentence,"c":comment,
        "p1":p1,"p2":p2,"p3":p3,"p4":p4,"page":page,"len":len(vip_post),
        "post_zan":post_zan,"username":username,
    "post_fav":post_fav})

"""入站必看模板函数1"""
def must_see_blog_posts(request):

    now_time = datetime.datetime.now()
    # 当前天 显示当前日期是本周第几天
    day_num = now_time.isoweekday()
    # 计算当前日期所在周一
    week_day = (now_time - datetime.timedelta(days=day_num))

    post_zan = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by('-zan')[:5]  # 点赞文章

    post_fav = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by('-number_of_favorites')[:5]  # 本周最多收藏

    top_loop=Post.objects.filter(post_private=False).filter(false_delete=False).order_by("-look")[:5]

    try:
        ran = random.randint(0, len(Sentence.objects.all()) - 1)  # 随机获取一条
    except:
        ran=None

    sentence = Sentence.objects.all()[ran]  # 每日一句
    sentence.time = timezone.now()


    p1 = Post.objects.filter(post_private=False).filter(false_delete=False).values('author').distinct().count()  # 统计作者
    p2 = Post.objects.filter(post_private=False).filter(false_delete=False).all().count()  # 统计文章
    p3 = Comment.objects.count()  # 统计评论
    p4 = Message.objects.all().count()  # 统计留言

    comment = Comment.objects.order_by('-time')[:5]

    username=request.session.get("username")
    username=Login.objects.filter(username=username).first()

    return render(request,'must_see_blog_posts.html',context={
        "s":sentence,"c":comment,"p1":p1,"p2":p2,"p3":p3,"p4":p4,
            "post_zan":post_zan,"top_loop":top_loop,"post_fav":post_fav,
        "username":username
    })

"""入站必看模板函数2"""
def must_see_blog_posts2(request):

    now_time = datetime.datetime.now()
    # 当前天 显示当前日期是本周第几天
    day_num = now_time.isoweekday()
    # 计算当前日期所在周一
    week_day = (now_time - datetime.timedelta(days=day_num))

    post_zan = Post.objects.filter(post_private=False).filter(false_delete=False).order_by('-zan')[:5]  # 点赞文章

    top_zan=Post.objects.filter(post_private=False).filter(false_delete=False).order_by("-zan")[:5]

    try:
        ran = random.randint(0, len(Sentence.objects.all()) - 1)  # 随机获取一条
    except:
        ran=None
    sentence = Sentence.objects.all()[ran]  # 每日一句
    sentence.time = timezone.now()

    p1 = Post.objects.filter(post_private=False).filter(false_delete=False).values('author').distinct().count()  # 统计作者
    p2 = Post.objects.filter(post_private=False).filter(false_delete=False).all().count()  # 统计文章
    p3 = Comment.objects.count()  # 统计评论
    p4 = Message.objects.all().count()  # 统计留言

    comment = Comment.objects.order_by('-time')[:5]

    username=request.session.get("username")
    username=Login.objects.filter(username=username).first()
    return render(request,'must_see_blog_posts2.html',context={
        "s":sentence,"c":comment,"p1":p1,"p2":p2,"p3":p3,"p4":p4,
            "post_zan":post_zan,"top_zan":top_zan,"username":username})

"""入站必看模板函数3"""
def must_see_blog_posts3(request):

    now_time = datetime.datetime.now()
    # 当前天 显示当前日期是本周第几天
    day_num = now_time.isoweekday()
    # 计算当前日期所在周一
    week_day = (now_time - datetime.timedelta(days=day_num))

    post_zan = Post.objects.filter(post_private=False).filter(false_delete=False).order_by('-number_of_favorites')[:5]  # 点赞文章

    top_cai=Post.objects.filter(post_private=False).filter(false_delete=False).order_by("-cai")[:5]

    try:
        ran = random.randint(0, len(Sentence.objects.all()) - 1)  # 随机获取一条
    except:
        ran=None

    sentence = Sentence.objects.all()[ran]  # 每日一句
    sentence.time = timezone.now()

    p1 = Post.objects.filter(post_private=False).filter(false_delete=False).values('author').distinct().count()  # 统计作者
    p2 = Post.objects.filter(post_private=False).filter(false_delete=False).all().count()  # 统计文章
    p3 = Comment.objects.count()  # 统计评论
    p4 = Message.objects.all().count()  # 统计留言

    comment = Comment.objects.order_by('-time')[:5]
    username=request.session.get("username")
    username=Login.objects.filter(username=username).first()

    return render(request,'must_see_blog_posts3.html',context={
        "s":sentence,"c":comment,"p1":p1,"p2":p2,"p3":p3,"p4":p4,
            "post_zan":post_zan,"top_cai":top_cai,"username":username})


"""发送消息"""
def send(request):
    ret=renzheng(request)
    if ret==-1:
        return HttpResponse("未登录")

    try:
        receiver=request.POST.get("receiver")
        content=request.POST.get("content")

        send_user=Login.objects.filter(username=request.session.get("username")).first()
        receiver_user=Login.objects.filter(id=receiver).first()

        f=FriendShip.objects.filter(followed=receiver_user,follower=send_user).first()
        FriendShip.add_unread(f)
    #我是被关注对象，对方是关注对象
    except:
        pass
    try:
        chat=Chat()
        chat.author=send_user
        chat.receiver=receiver_user
        chat.content=content
        chat.save()
    except:
        return HttpResponse(-1)
    else:
        return HttpResponse(1)

"""接收消息"""
def getting_information(request):
    ret=renzheng(request)
    if ret==-1:
        return HttpResponse("未登录")
    username=request.session.get("username")
    username=request.session.get("username")
    L=Login.objects.filter(username=username).first()
    id=request.POST.get("id")
    char_user=Chat.objects.filter(author_id=id,receiver=L,readflag=False)
    for i in char_user:
        Chat.objects.filter(id=i.id).update(readflag=True)


    data_list = []
    # 将评论数据构造成列表

    for com in char_user:
        dic = {}

        dic["pic"] = str(Login.objects.filter(id=id).first().avatar)# 发送方头像

        dic["time"] = com.time.strftime('%Y-%m-%d %H:%M:%S')  # 时间
        dic["content"] = com.content# 发送内容
        data_list.append(dic)

    return JsonResponse({"data": data_list})

"""ta的主页"""
def his_homepage(request,id):


    uer_obj=Login.objects.filter(id=id).first()

    uer_post=len(Post.objects.filter(post_private=False).filter(false_delete=False).filter(author=uer_obj))#获该用户的所有发布的文章

    user_momment=len(Comment.objects.filter(username=uer_obj))#获该用户的所有评论

    user_message=len(Message.objects.filter(username=uer_obj))#获该用户的所有评论


    user_followed=len(FriendShip.objects.filter(followed=uer_obj))#获该用户的所有关注个数


    user_follower=len(FriendShip.objects.filter(follower=uer_obj))#获取用户的所有粉丝个数

    return render(request,"his_homepage.html",context={
    "uer_obj":uer_obj,"uer_post":uer_post,"user_momment":user_momment,
    "user_message":user_message,"user_followed":user_followed,"user_follower":user_follower
    })

"""ta的文章"""
def her_post(request,id):


    uer_obj=Login.objects.filter(id=id).first()

    uer_post=(Post.objects.filter(post_private=False).filter(false_delete=False).filter(author=uer_obj))#获该用户的所有发布的文章
    try:
        ran = random.randint(0, len(Sentence.objects.all()) - 1)  # 随机获取一条
    except:
        ran=None
    sentence = Sentence.objects.all()[ran]  # 每日一句
    sentence.time = timezone.now()

    p1 = Post.objects.filter(post_private=False).filter(false_delete=False).values('author').distinct().count()  # 统计作者
    p2 = Post.objects.filter(post_private=False).filter(false_delete=False).all().count()  # 统计文章
    p3 = Comment.objects.count()  # 统计评论
    p4 = Message.objects.all().count()  # 统计留言

    comment = Comment.objects.order_by('-time')[:5]
    now_time = datetime.datetime.now()
    # 当前天 显示当前日期是本周第几天
    day_num = now_time.isoweekday()
    # 计算当前日期所在周一
    week_day = (now_time - datetime.timedelta(days=day_num))

    username = request.session.get("username")
    username = Login.objects.filter(username=username).first()

    post_zan = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by(
        '-zan')[
               :5]  # 点赞文章
    post_fav = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by(
        '-number_of_favorites')[:5]  # 本周最多收藏



    return render(request,'her_post.html',context={"post1":uer_post,"s": sentence,
        "c": comment, "p1": p1, "p2": p2,"p3": p3, "p4": p4,"username":username,
        "post_zan":post_zan ,"post_fav":post_fav,
                                                  })

"""ta的评论函数"""
def her_comment(request,id):

    uer_obj=Login.objects.filter(id=id)

    user_momment=(Comment.objects.filter(username=uer_obj))#获该用户的所有评论

    user_message=(Message.objects.filter(username=uer_obj))#获该用户的所有留言
    try:
        ran = random.randint(0, len(Sentence.objects.all()) - 1)  # 随机获取一条
    except:
        ran=None
    sentence = Sentence.objects.all()[ran]  # 每日一句
    sentence.time = timezone.now()

    p1 = Post.objects.filter(post_private=False).filter(false_delete=False).values('author').distinct().count()  # 统计作者
    p2 = Post.objects.filter(post_private=False).filter(false_delete=False).all().count()  # 统计文章
    p3 = Comment.objects.count()  # 统计评论
    p4 = Message.objects.all().count()  # 统计留言

    comment = Comment.objects.order_by('-time')[:5]
    now_time = datetime.datetime.now()
    # 当前天 显示当前日期是本周第几天
    day_num = now_time.isoweekday()
    # 计算当前日期所在周一
    week_day = (now_time - datetime.timedelta(days=day_num))

    username = request.session.get("username")
    username = Login.objects.filter(username=username).first()

    post_zan = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by(
        '-zan')[
               :5]  # 点赞文章
    post_fav = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by(
        '-number_of_favorites')[:5]  # 本周最多收藏

    return render(request,'her_comment.html',context={"user_momment":user_momment,
    "user_message":user_message,"s": sentence, "c": comment, "p1": p1, "p2": p2,
         "p3": p3, "p4": p4,"username":username,"post_zan":post_zan
         ,"post_fav":post_fav


                                                     })

"""ta的粉丝"""
def her_fensi(request,id):

    uer_obj=Login.objects.filter(id=id)

    user_fensi=(FriendShip.objects.filter(follower=uer_obj))
    list=[]
    for i in user_fensi:
        p = Login.objects.filter(id=i.followed_id).first()
        list.append(p)


    try:
        ran = random.randint(0, len(Sentence.objects.all()) - 1)  # 随机获取一条
    except:
        ran=None
    sentence = Sentence.objects.all()[ran]  # 每日一句
    sentence.time = timezone.now()

    p1 = Post.objects.filter(post_private=False).filter(false_delete=False).values('author').distinct().count()  # 统计作者
    p2 = Post.objects.filter(post_private=False).filter(false_delete=False).all().count()  # 统计文章
    p3 = Comment.objects.count()  # 统计评论
    p4 = Message.objects.all().count()  # 统计留言

    comment = Comment.objects.order_by('-time')[:5]
    now_time = datetime.datetime.now()
    # 当前天 显示当前日期是本周第几天
    day_num = now_time.isoweekday()
    # 计算当前日期所在周一
    week_day = (now_time - datetime.timedelta(days=day_num))

    username = request.session.get("username")
    username = Login.objects.filter(username=username).first()

    post_zan = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by(
        '-zan')[
               :5]  # 点赞文章
    post_fav = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by(
        '-number_of_favorites')[:5]  # 本周最多收藏

    return render(request,'her_fensi.html',context={"user_fensi":list,
            "s": sentence, "c": comment, "p1": p1, "p2": p2,
            "p3": p3, "p4": p4, "username": username, "post_zan": post_zan
            , "post_fav": post_fav
                                                        })

"""ta的关注"""
def her_guanzhu(request,id):


    uer_obj=Login.objects.filter(id=id)

    user_friendship=(FriendShip.objects.filter(followed=uer_obj))#获该用户的所有关注

    list=[]
    for i in user_friendship:
        p = Login.objects.filter(id=i.follower_id).first()
        list.append(p)
    try:
        ran = random.randint(0, len(Sentence.objects.all()) - 1)  # 随机获取一条
    except:
        ran=None

    sentence = Sentence.objects.all()[ran]  # 每日一句
    sentence.time = timezone.now()

    p1 = Post.objects.filter(post_private=False).filter(false_delete=False).values('author').distinct().count()  # 统计作者
    p2 = Post.objects.filter(post_private=False).filter(false_delete=False).all().count()  # 统计文章
    p3 = Comment.objects.count()  # 统计评论
    p4 = Message.objects.all().count()  # 统计留言

    comment = Comment.objects.order_by('-time')[:5]
    now_time = datetime.datetime.now()
    # 当前天 显示当前日期是本周第几天
    day_num = now_time.isoweekday()
    # 计算当前日期所在周一
    week_day = (now_time - datetime.timedelta(days=day_num))

    username = request.session.get("username")
    username = Login.objects.filter(username=username).first()

    post_zan = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by(
        '-zan')[
               :5]  # 点赞文章
    post_fav = Post.objects.filter(post_private=False).filter(false_delete=False).filter(pub_time__range=(week_day, now_time)).order_by(
        '-number_of_favorites')[:5]  # 本周最多收藏

    return render(request,'her_guanzhu.html',context={"user_friendship":list,
            "s": sentence, "c": comment, "p1": p1, "p2": p2,
            "p3": p3, "p4": p4, "username": username, "post_zan": post_zan
            , "post_fav": post_fav
                                                        })

"""忘记密码1"""
def forget_password_one(request):
    id=request.POST.get("id")
    email=request.POST.get("email")
    try:
        L=Login.objects.filter(username=id).first()
    except BaseException:
        return  HttpResponse(0)#用户不存在

    else:
        if not L:
            return HttpResponse(0)#用户不存在
        if L.email!=email:
            return HttpResponse(-1)#输入的密码和email不匹配

        rand4 = str(random.randint(1000, 9999))
        from django.core.mail import send_mail
        from web import settings

        try:
            html_message = "验证码：{}".format(rand4)

            send_mail('个人博客用户注册邮箱验证码', '个人博客', settings.EMAIL_FROM,
                      ['{}'.format(email)], html_message=html_message, fail_silently=False
                      )
        except Exception:
            return HttpResponse(2)#发送邮件失败
        else:
            request.session["email_pass"]=rand4

        return HttpResponse(1)

""" 忘记密码2"""
def  forget_password_two(request):
    email_code=request.POST.get("email")#获取ajax发送过来的验证码
    email_pass=request.session.get("email_pass") #获取保证在session中的邮箱验证码
    print(email_code,email_pass,7744745454)
    if email_pass!=email_code:
        return HttpResponse(-1)#验证码错误
    else:
        return HttpResponse(1)#验证成功

"""忘记密码3"""
def forget_password_three(request):
    password1=request.POST.get("password1")
    password2=request.POST.get("password2")
    if password1!=password2:
        return HttpResponse(-1)
    password1 = make_password(password1)
    username=request.session.get("username")

    Login.objects.update_or_create(username=username, defaults={'password': password1})

    return HttpResponse(1)
