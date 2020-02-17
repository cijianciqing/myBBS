from django.test import TestCase

# Create your tests here.

import os
import django
import logging
from myBBS import settings


if __name__ == '__main__':
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myBBS.settings')
   django.setup()

   from myarticle import models
   from myauth.models import MyUserInfo
   from django.db.models import Count
   from guardian.shortcuts import assign_perm

   user01 = MyUserInfo.objects.filter(username='aaaaa01').first()
   # blog = user.blog
   # # 查询文章分类及对应的文章数
   # category_list = models.Category.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c")
   # print(category_list)
   article01 = models.Article.objects.all().first()
   assign_perm('add_article', user01, article01)
   result = user01.has_perm('add_article', article01)
   print(result)
