"""myBBS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path,include,re_path
from django.conf import settings
from django.views import static
from django.conf.urls import url
from django.views.generic import TemplateView, RedirectView
from django.views.static import serve
from . import views
app_name = 'myblog'

urlpatterns = [
    path('index/',views.index,name='index'),
    ##################
    # 文章操作，增删改查
    ##################
    path('createArticle/',views.createArticle,name='createArticle'),
    re_path(r'^editArticle/(?P<articleID>\d+)/$',views.editArticle,name='editArticle'),
    re_path(r'^deleteArticle/(?P<articleID>\d+)/$', views.deleteArticle, name='deleteArticle'),
    # 打开特定文章
    # re_path(r'^article/(?P<username>[a-zA-Z0-9_]{4,19})?/article/(?P<articleID>\d+)/$',views.articleDetail,name='articleDetail'),
    re_path(r'^article/(?P<articleID>\d+)/$', views.articleDetail, name='articleDetail'),

    ##################
    #标签操作，增删改查
    ##################
    #获取标签对应的文章
    re_path(r'^tagToArticles/(?P<tagID>\d+)/$',views.tagToArticle, name='tagToArticles'),

    ##################
    #分类操作，增删改查
    ##################
    #获取分类对应的文章

    # 点赞
    path('thumbup/',views.thumbUp,name='thumbUp'),


    # 评论的操作
    # 提交评论
    path('postComment/', views.postComment, name='postComment'),
    # 获取某个文章的评论数据
    re_path(r'^getCommentTreeData/(?P<articleID>\d+)/$', views.getCommentTreeData, name='getCommentTreeData'),


    # 进入特定用户博客
    re_path(r'^(?P<username>[a-zA-Z0-9_]{3,19})/$', views.user,name='user'),


]
