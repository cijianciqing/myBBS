import json
from bs4 import BeautifulSoup
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from myarticle import models
from myauth.models import MyUserInfo
# Create your views here.
from utils.myResponse import wrap_json_response, ReturnCode
from django.db.models import Count
from . import forms
from django.contrib.auth.decorators import login_required

#进入系统首页
def index(request):
    # 查询所有的文章列表
    article_list = models.Article.objects.all()
    return render(request, "index.html", {"article_list": article_list})

# 进入用户的博客首页
@login_required
def user(request, username):
    print(username)
    # 获取文章作者 所有的文章
    user = MyUserInfo.objects.get(username=username)
    userArticles = models.Article.objects.filter(user=user)
    # 查询文章作者文章的 分类及对应的文章数
    category_list = models.Category.objects.filter(blog=user.blog).annotate(c=Count("article")).values("title", "c")
    return render(request,'myarticle/blogPage.html',context={
        # 'user': user,
        # 'username': username,
        'blogUser': user,
        'userArticles': userArticles,
        'category_list': category_list
        # 'userCatalogs': userCatalogs,
    })

# 文章详情页面
def articleDetail(request, articleID):
    # print('#$'*100)
    # print(articleID)
    # print(request.user.username)
    # print('#$' * 100)
    # 获取文章的作者
    user = models.Article.objects.get(pk = articleID).user
    userArticle = models.Article.objects.get(pk=articleID)
    # articleDetail = models.ArticleDetail.objects.get(article=userArticle)

    # 获取文章A分类中,文章作者的文章
    article_list = models.Article.objects.filter(user=user,category=userArticle.category)

    # 获取当前登录用户对于此文章的点赞信息
    articleUpDown = models.ArticleUpDown(article=userArticle, user=MyUserInfo(username='mytestuser'))
    # 判断用户是否已登录
    if isinstance(request.user,AnonymousUser) :
        pass
    else:
        try:
            articleUpDown = models.ArticleUpDown.objects.get(article=userArticle,user=request.user)
        except Exception as e:
            articleUpDown = models.ArticleUpDown(article=userArticle,user=request.user)

    # userCatalogs = models.Category.objects.filter(blog=userBlog)
    # userTags = models.Tag.objects.filter(blog=userBlog)
    return render(request, 'myarticle/articlePage.html', context={
        # 'user': user,
        # 'username': user.username,
        'blogUser': user,# 文章的作者
        'userArticle': userArticle,
        # 'articleDetail': articleDetail,
        "articleUpDown": articleUpDown,
        'article_list': article_list
        # 'userCatalogs': userCatalogs,
    })

# 文章点赞功能
@login_required
@transaction.atomic
def thumbUp(request):
    article_id = request.POST.get('article_id')
    # 此处注意转换，从json string转换为boolean
    is_up = json.loads(request.POST.get('is_up'))
    user = request.user
    try:
       models.ArticleUpDown.objects.get(article_id=article_id, user=request.user)
    except Exception as e:
       models.ArticleUpDown.objects.create(user=user, article_id=article_id)

    models.ArticleUpDown.objects.filter(user=user, article_id=article_id).update( is_up=is_up)
    # 更新点赞表
    if is_up:
        models.Article.objects.filter(pk=article_id).update(up_count=F("up_count") + 1)
    else:
        models.Article.objects.filter(pk=article_id).update(up_count=F("up_count") - 1)
    thumbCount = models.Article.objects.get(pk=article_id).up_count
    myResponseData = wrap_json_response(data={"thumbCount":thumbCount},code=ReturnCode.SUCCESS,message=is_up)
    return JsonResponse(data=myResponseData,safe=False)

# 获取文章的所有评论
def getCommentTreeData(request,articleID):
    # 需要使用list将querySet更换成对象
    ret = list(models.Comment.objects.filter(article_id=articleID).extra(
        select={"create_time_new": "date_format(myarticle_comment.create_time,'%%Y-%%m-%%d %%H:%%i:%%s')"}).
               values("pk", "content", "parent_comment_id", "create_time_new", "user__username"))
        #extra:select对create_time进行格式化
    return JsonResponse(data=ret, safe=False)

# 添加评论
@login_required
@transaction.atomic
def postComment(request):
    pid = request.POST.get("pid")
    article_id = request.POST.get("article_id")
    content = request.POST.get("content")
    user_pk = request.user.pk
    response = {}
    if not pid:  # 根评论
        comment_obj = models.Comment.objects.create(article_id=article_id, user_id=user_pk, content=content)
    else:   #子评论
        comment_obj = models.Comment.objects.create(article_id=article_id, user_id=user_pk, content=content,
                                                    parent_comment_id=pid)

    models.Article.objects.filter(pk=article_id).update(comment_count=F("comment_count") + 1)

    myResponseData = wrap_json_response(code=ReturnCode.SUCCESS, message='success')
    return JsonResponse(data=myResponseData)

# 创建文章
@login_required
@transaction.atomic
def createArticle(request):
    if request.method == 'GET':
        currentUser = request.user
        articleForm = forms.CreateArticleForm(False,currentUser)
        # articleForm.fields.widget.choices
        # articleForm.
        #currentArticleID: 用于编辑前端页面时使用，否则创建文章时会报错，在创建文章时无实际意义
        return render(request, 'myarticle/createArticle.html', {'form_obj': articleForm,'currentArticleID': 0})
    else:
        title = request.POST.get("title")
        category = request.POST.get("category")
        content = request.POST.get("content")
        # 获取文章的description
        bs = BeautifulSoup(content, 'html.parser')
        myDescription = bs.text[0:150]
        # 获取文章的tags
        tags = request.POST.get("tags")
        tags = json.loads(tags)
        newTags= []
        for tag in tags:
            newTags.append(int(tag))
        myTags = models.Tag.objects.filter(nid__in=newTags)
        newArticle = models.Article.objects.create(title=title,category_id=category,content=content,user=request.user,desc=myDescription)
        newArticle.tags.set(myTags)
        # 创建成功后，转到当前用户的blog
        myUrl = reverse("myblog:user", kwargs={"username": request.user.username})

        print("myarticle.views.createArticle:",myUrl)
        myResponseData = wrap_json_response(code=ReturnCode.SUCCESS, message=myUrl)
        return JsonResponse(data=myResponseData)


# 编辑文章
@login_required
@transaction.atomic
def editArticle(request,articleID):
    if request.method == 'GET':
        currentUser = request.user
        currentArticle = get_object_or_404(models.Article,pk=articleID)
        articleForm = forms.CreateArticleForm(True,currentUser,instance=currentArticle)
        return render(request, 'myarticle/createArticle.html', {'form_obj': articleForm,'currentArticleID': currentArticle.pk})
    else:
        title = request.POST.get("title")
        category = request.POST.get("category")
        content = request.POST.get("content")
        # 获取文章的description
        bs = BeautifulSoup(content, 'html.parser')
        myDescription = bs.text[0:150]
        # 获取文章的tags
        tags = request.POST.get("tags")
        tags = json.loads(tags)
        newTags= []
        for tag in tags:
            newTags.append(int(tag))
        myTags = models.Tag.objects.filter(nid__in=newTags)
        models.Article.objects.filter(pk=articleID).update(title=title,category_id=category,content=content,user=request.user,desc=myDescription)
        models.Article.objects.filter(pk=articleID).first().tags.set(myTags)
        # 创建成功后，转到当前用户的blog
        myUrl = reverse("myblog:user", kwargs={"username": request.user.username})
        # print("myarticle.views.createArticle:",myUrl)
        myResponseData = wrap_json_response(code=ReturnCode.SUCCESS, message=myUrl)
        return JsonResponse(data=myResponseData)

# 删除文章
@login_required
@transaction.atomic
def deleteArticle(request,articleID):
    myDeleteArticle = get_object_or_404(models.Article, pk=articleID)
    if(request.user.username == myDeleteArticle.user.username):
        models.Article.objects.get(pk=articleID).delete()
        myUrl = reverse("myblog:user", kwargs={"username":request.user.username})
        return redirect(to=myUrl)
    else:
        exceptionMessage="Warning: "+request.user.username+" 没有此文档的删除权限!!!"
        raise PermissionDenied(exceptionMessage)