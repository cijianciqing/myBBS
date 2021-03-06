import datetime

from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
from myBBS import settings
import os


class MyUserInfo(AbstractUser):
    """
    用户信息表
    """
    nid = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=11, null=True, unique=True)
    avatar = models.ImageField(upload_to="avatars/", default='avatars/default.png', verbose_name="头像")
    create_time = models.DateTimeField(auto_now_add=True)

    blog = models.OneToOneField(to="myarticle.Blog", to_field="nid", null=True,on_delete=models.SET_NULL)

    def __str__(self):
        return self.username

    @property
    def avatarURL(self):
        return self.avatar.url

def get_custom_anon_user(User):
    return User(
        username='AnonymousUser',
        create_time=datetime.datetime(2020, 1, 1),
    )
