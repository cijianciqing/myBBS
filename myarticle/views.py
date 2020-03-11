import json
from bs4 import BeautifulSoup
from django.contrib.auth.models import AnonymousUser
from django.core.paginator import Paginator
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F, Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from myarticle import models
from myauth.models import MyUserInfo
# Create your views here.
from utils.myResponse import wrap_json_response, ReturnCode
from django.db.models import Count
from . import forms
from django.contrib.auth.decorators import login_required
from myBBS import settings


# 进入系统首页
def index(request):
    # 查询所有的文章列表
    article_list = models.Article.objects.all()[0:9]
    catelgory_list = models.Category.objects.all()
    return render(request, "index.html", {"article_list": article_list,
                                          "catelgory_list": catelgory_list})


# 文章的查询
def searchArticle(request):
    searchInfo = request.GET.get("searchInfo")
    # 用于区分站点内搜索和全局搜索
    # 对于全局搜索，username=searchInfo,对于博客内搜索，username=username
    username = request.GET.get("username", "")
    print('username in myarticle.views.searchArticle: ', username)


    myfilter = Q(title__icontains=searchInfo) | Q(desc__icontains=searchInfo) | Q(user__username__icontains=searchInfo)
    # 设置搜索文章的分类
    wqn_category = int(request.GET.get("category", 9999))
    if wqn_category != 9999:
        myfilter = Q(
            Q(title__icontains=searchInfo) | Q(desc__icontains=searchInfo) | Q(user__username__icontains=searchInfo)) & Q(
            category__nid__exact=wqn_category)

    if username != '':
        # 用于blog内搜索
        articleList = list(models.Article.objects.filter(
            Q(Q(title__icontains=searchInfo) | Q(desc__icontains=searchInfo)) & Q(user__username__exact=username)).
                           extra(
            select={"create_time_new": "date_format(myarticle_article.create_time,'%%Y-%%m-%%d %%H:%%i:%%s')",
                    "avatarURL": "concat(%s,avatar)",
                    "username": "username"},
            select_params=(settings.MEDIA_URL,)).
                           values("pk", "title", "create_time_new", "desc", "comment_count", "up_count", "user__phone",
                                  "avatarURL", "username"))
    else:
        # 用于全局搜索
        articleList = list(models.Article.objects.filter(myfilter).
                           extra(
            select={"create_time_new": "date_format(myarticle_article.create_time,'%%Y-%%m-%%d %%H:%%i:%%s')",
                    "avatarURL": "concat(%s,avatar)",
                    "username": "username"},
            select_params=(settings.MEDIA_URL,)).
                           values("pk", "title", "create_time_new", "desc", "comment_count", "up_count", "user__phone",
                                  "avatarURL", "username"))


    paginator = Paginator(articleList, 10)
    # 获取所有文章的总页数
    page_total_num = paginator.num_pages

    # 页面上的search按钮，进行搜索时，需要有个默认值
    startPageNum = request.GET.get("startPageNum",1)
    # 获取某页（page）的所有文章
    page_article_list = list(paginator.page(startPageNum))

    myResponseData = wrap_json_response(data={"articleList": page_article_list,
                                              "page_total_num": page_total_num,
                                              "startPageNum": startPageNum
                                              }, code=ReturnCode.SUCCESS)
    return JsonResponse(data=myResponseData, safe=False)


# 进入用户的博客首页
@login_required
def user(request, username):
    # print(username)
    # 获取文章作者 所有的文章
    user = MyUserInfo.objects.get(username=username)
    userArticles = models.Article.objects.filter(user=user)
    # 查询文章作者文章的 分类及对应的文章数
    category_list = models.Category.objects.filter(article__user=user).annotate(c=Count("article")).values("nid",
                                                                                                           "title", "c")
    # 查询文章作者的标签
    tag_list = models.Tag.objects.filter(blog=user.blog).values('nid', 'title')
    # print(tag_list)
    return render(request, 'myarticle/blogPage.html', context={
        # 'user': user,
        # 'username': username,
        'blogUser': user,
        'userArticles': userArticles,
        'category_list': category_list,
        'tag_list': tag_list
        # 'userCatalogs': userCatalogs,
    })


# 进入标签的页面
def tagToArticle(request, username, tagID):
    myTag = models.Tag.objects.get(pk=tagID)
    myUser = MyUserInfo.objects.get(username=username)
    # 获取标签id对应的文档
    tagArticles = serializers.serialize("json", models.Article.objects.filter(tags=myTag,user=myUser))
    # 获取标签对应的用户
    # tag2User = tagArticles[0].user
    return JsonResponse(
        data={
            'tagArticles': tagArticles
        }, safe=False)



# 进入用户的特定分类页面
# def categoryToArticles(request, categoryID, username):
def categoryToArticles(request, username):
    categoryID = request.GET.get("categoryID")
    print("myarticle.views.categoryToArticles:", categoryID)
    mycategory = models.Category.objects.get(pk=categoryID)
    # 获取博主此分类的文章
    user = MyUserInfo.objects.get(username=username)
    categoryToArticles = serializers.serialize("json", models.Article.objects.filter(user=user, category_id=categoryID))

    return JsonResponse(
        data={
            'categoryToArticles': categoryToArticles
        }, safe=False)



# 文章详情页面
def articleDetail(request, articleID):
    # 获取文章的作者
    user = models.Article.objects.get(pk=articleID).user
    userArticle = models.Article.objects.get(pk=articleID)
    # articleDetail = models.ArticleDetail.objects.get(article=userArticle)

    # 获取文章A分类中,文章作者的文章
    article_list = models.Article.objects.filter(user=user, category=userArticle.category)

    # 获取当前登录用户对于此文章的点赞信息
    articleUpDown = models.ArticleUpDown(article=userArticle, user=MyUserInfo(username='mytestuser'))
    # 判断用户是否已登录,并获取用户的点赞信息
    # if isinstance(request.user, AnonymousUser):
    if not request.user.is_authenticated:
        pass
    else:
        try:
            articleUpDown = models.ArticleUpDown.objects.get(article=userArticle, user=request.user)
        except Exception as e:
            articleUpDown = models.ArticleUpDown(article=userArticle, user=request.user)

        myCommentForm = forms.CommentForm()
    return render(request, 'myarticle/articlePage.html', context={
        # 'user': user,
        # 'username': user.username,
        'blogUser': user,  # 文章的作者
        'userArticle': userArticle,
        # 'articleDetail': articleDetail,
        "articleUpDown": articleUpDown,
        'article_list': article_list,
        'myCommentForm': myCommentForm
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

    models.ArticleUpDown.objects.filter(user=user, article_id=article_id).update(is_up=is_up)
    # 更新点赞表
    if is_up:
        models.Article.objects.filter(pk=article_id).update(up_count=F("up_count") + 1)
    else:
        models.Article.objects.filter(pk=article_id).update(up_count=F("up_count") - 1)
    thumbCount = models.Article.objects.get(pk=article_id).up_count
    myResponseData = wrap_json_response(data={"thumbCount": thumbCount}, code=ReturnCode.SUCCESS, message=is_up)
    return JsonResponse(data=myResponseData, safe=False)


# 获取文章的所有评论
def getCommentTreeData(request, articleID):
    # 需要使用list将querySet更换成对象
    ret = list(models.Comment.objects.filter(article_id=articleID).extra(
        select={"create_time_new": "date_format(myarticle_comment.create_time,'%%Y-%%m-%%d %%H:%%i:%%s')",
                "avatarURL": "concat(%s,avatar)", },
        select_params=(settings.MEDIA_URL,)
    ).values("pk", "content", "parent_comment_id", "create_time_new",
             "user__username", "avatarURL"))
    # extra:select对create_time进行格式化
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
    else:  # 子评论
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
        articleForm = forms.CreateArticleForm(False, currentUser)
        # currentArticleID: 用于编辑前端页面时使用，否则创建文章时会报错，在创建文章时无实际意义
        return render(request, 'myarticle/createArticle.html', {'form_obj': articleForm, 'currentArticleID': 0})
    else:

        form_obj = forms.CreateArticleForm(True, request.user, request.POST)
        if form_obj.is_valid():
            # print("formOBJ in createArticle: ",type(form_obj.cleaned_data))
            # print(form_obj.cleaned_data)
            myTags = form_obj.cleaned_data.get("tags")
            form_obj.cleaned_data.pop("tags")
            newArticle = models.Article.objects.create(**form_obj.cleaned_data, user=request.user)
            newArticle.tags.set(myTags)
            myUrl = reverse("myblog:user", kwargs={"username": request.user.username})
            myResponseData = wrap_json_response(code=ReturnCode.SUCCESS, message=myUrl)
            return JsonResponse(data=myResponseData)
        else:
            myResponseData = wrap_json_response(data=form_obj.errors, code=ReturnCode.FAILED)
            return JsonResponse(data=myResponseData)


# 编辑文章
@login_required
@transaction.atomic
def editArticle(request, articleID):
    if request.method == 'GET':
        currentUser = request.user
        currentArticle = get_object_or_404(models.Article, pk=articleID)
        articleForm = forms.CreateArticleForm(True, currentUser, instance=currentArticle)
        return render(request, 'myarticle/createArticle.html',
                      {'form_obj': articleForm, 'currentArticleID': currentArticle.pk})
    else:
        form_obj = forms.CreateArticleForm(True, request.user, request.POST)
        if form_obj.is_valid():
            # print("formOBJ in createArticle: ",type(form_obj.cleaned_data))
            # print(form_obj.cleaned_data)
            myTags = form_obj.cleaned_data.get("tags")
            form_obj.cleaned_data.pop("tags")
            models.Article.objects.filter(pk=articleID).update(**form_obj.cleaned_data, user=request.user)
            models.Article.objects.filter(pk=articleID).first().tags.set(myTags)

            myUrl = reverse("myblog:user", kwargs={"username": request.user.username})
            myResponseData = wrap_json_response(code=ReturnCode.SUCCESS, message=myUrl)
            return JsonResponse(data=myResponseData)
        else:
            myResponseData = wrap_json_response(data=form_obj.errors, code=ReturnCode.FAILED)
            return JsonResponse(data=myResponseData)

# 删除文章
@login_required
@transaction.atomic
def deleteArticle(request, articleID):
    myDeleteArticle = get_object_or_404(models.Article, pk=articleID)
    if (request.user.username == myDeleteArticle.user.username):
        models.Article.objects.get(pk=articleID).delete()
        myUrl = reverse("myblog:user", kwargs={"username": request.user.username})
        return redirect(to=myUrl)
    else:
        exceptionMessage = "Warning: " + request.user.username + " 没有此文档的删除权限!!!"
        raise PermissionDenied(exceptionMessage)

# 添加标签
@login_required
def addTag(request):
    tagname = request.POST.get('tag', '')
    tag = models.Tag.objects.create(title=tagname,blog=request.user.blog)
    return JsonResponse(data={'tag':tag.tag2Json()},safe=False)