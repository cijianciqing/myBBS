import json

from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render
from myarticle import models
from myauth.models import MyUserInfo
# Create your views here.
from utils.myResponse import wrap_json_response, ReturnCode


def index(request):
    # 查询所有的文章列表
    article_list = models.Article.objects.all()
    return render(request, "index.html", {"article_list": article_list})


def user(request,username):
    print('#$1' * 100)
    print(username)
    print('#$1' * 100)
    user = MyUserInfo.objects.get(username=username)
    userBlog = user.blog
    userArticles = models.Article.objects.filter(user=user)
    # userCatalogs = models.Category.objects.filter(blog=userBlog)
    # userTags = models.Tag.objects.filter(blog=userBlog)
    return render(request,'myarticle/userPage.html',context={
        # 'user': user,
        'username': username,
        'userArticles': userArticles,
        # 'userCatalogs': userCatalogs,
    })


def articleDetail(request, username, articleID):
    print('#$'*100)
    print(username,articleID)
    print('#$' * 100)
    user = MyUserInfo.objects.get(username=username)
    userBlog = user.blog
    userArticle = models.Article.objects.get(pk=articleID)
    articleDetail = models.ArticleDetail.objects.get(article=userArticle)
    try:
        articleUpDown = models.ArticleUpDown.objects.get(article=userArticle,user=request.user)
    except Exception as e:
        articleUpDown = models.ArticleUpDown(article=userArticle,user=request.user)

    # userCatalogs = models.Category.objects.filter(blog=userBlog)
    # userTags = models.Tag.objects.filter(blog=userBlog)
    return render(request, 'myarticle/articleDetail.html', context={
        # 'user': user,
        'username': username,
        'userArticle': userArticle,
        'articleDetail': articleDetail,
        "articleUpDown": articleUpDown
        # 'userCatalogs': userCatalogs,
    })

# 文章点赞功能
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