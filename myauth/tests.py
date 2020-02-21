from django.test import TestCase

# Create your tests here.
from django.core.paginator import Paginator
import os
import django
import logging
from myBBS import settings

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myBBS.settings')
    django.setup()

    from myarticle import models
    from myauth.models import MyUserInfo
    from django.db.models import Count, Q, F
    from guardian.shortcuts import assign_perm

    searchInfo ='a'
    articleList = list(models.Article.objects.filter(
        Q(Q(title__icontains=searchInfo) | Q(desc__icontains=searchInfo)) & Q(user__username__icontains=searchInfo)).
                       extra(
        select={"create_time_new": "date_format(myarticle_article.create_time,'%%Y-%%m-%%d %%H:%%i:%%s')",
                "avatarURL": "concat(%s,avatar)",
                "username": "username"},
        select_params=(settings.MEDIA_URL,)).
                       values("pk", "title", "create_time_new", "desc", "comment_count", "up_count", "user__phone",
                              "avatarURL", "username"))
    print(articleList[0])
    paginator = Paginator(articleList, 2)
    # 获取所有文章的总页数
    page_total_num = paginator.num_pages
    print(page_total_num)
    # 获取某页（page）的所有文章
    page_article_list = paginator.page(1)
    print(page_article_list[0])

    # result = Q(title__icontains='aaa') | Q(desc__icontains='bbb')
    # print(type(result))
    # print(result)
    # models.Category.objects.filter()
    # result = models.Comment.objects.
    # filter(article_id=4).extra(
    #     select={"create_time_new": "date_format(myarticle_comment.create_time,'%%Y-%%m-%%d %%H:%%i:%%s')",
    #             "avatarURL": "concat(%s,avatar)", },
    #     select_params=(settings.MEDIA_URL,)
    # ).values("pk", "content", "parent_comment_id", "create_time_new",
    #          "user__username", "avatarURL")
    # print(result)

    # user01 = MyUserInfo.objects.filter(username='aaaaa01').first()
    # blog = user.blog
    # # 查询文章分类及对应的文章数
    # category_list = models.Category.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c")
    # print(category_list)
    # article01 = models.Article.objects.all().first()
    # assign_perm('add_article', user01, article01)
    # result = user01.has_perm('add_article', article01)
    # print(result)

    # searchInfo = '22'
    # username = ''
    # print('username in myarticle.views.searchArticle: ', username)
    # articleList = []
    # if username != '':
    #     articleList = list(models.Article.objects.filter(
    #         Q(Q(title__icontains=searchInfo) | Q(desc__icontains=searchInfo)) & Q(user__username__exact=username)).
    #                        extra(
    #         select={"create_time_new": "date_format(myarticle_article.create_time,'%%Y-%%m-%%d %%H:%%i:%%s')",
    #                 "avatarURL": "concat(%s,avatar)",
    #                 "username": "username"},
    #         select_params=(settings.MEDIA_URL,)).
    #                        values("pk", "title", "create_time_new", "desc", "comment_count", "up_count", "user__phone",
    #                               "avatarURL", "username"))
    # else:
    #     articleList = list(
    #         models.Article.objects.filter(Q(title__icontains=searchInfo) | Q(desc__icontains=searchInfo)).
    #             extra(
    #             select={"create_time_new": "date_format(myarticle_article.create_time,'%%Y-%%m-%%d %%H:%%i:%%s')",
    #                     "avatarURL": "concat(%s,avatar)",
    #                     "username": "username"},
    #             select_params=(settings.MEDIA_URL,)).
    #             values("pk", "title", "create_time_new", "desc", "comment_count", "up_count", "user__phone", "avatarURL",
    #                    "username"))
    # print(articleList)
    # print(type(articleList))
