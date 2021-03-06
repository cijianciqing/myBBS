from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
# Create your models here.
from myauth.models import MyUserInfo

class Blog(models.Model):
    """
    博客信息
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)  # 个人博客标题
    # site = models.CharField(max_length=32, unique=True)  # 个人博客后缀
    theme = models.CharField(max_length=32)  # 博客主题

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "blog站点"
        verbose_name_plural = verbose_name


class Category(models.Model):
    """
    个人博客文章分类
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=32,unique=True)  # 分类标题
    # blog = models.ForeignKey(to="Blog", to_field="nid",null=True,on_delete=models.SET_NULL)  # 外键关联博客，一个博客站点可以有多个分类

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "文章分类"
        verbose_name_plural = verbose_name
        # unique_together = (("blog", "title"),)


class Tag(models.Model):
    """
    标签
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=32)  # 标签名
    blog = models.ForeignKey(to="Blog", to_field="nid",null=True,on_delete=models.SET_NULL)  # 所属博客

    def __str__(self):
        return self.title

    def tag2Json(self):
        return {"nid":self.nid,
                "title":self.title,
                "blog":self.blog_id
                }

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = verbose_name
        unique_together=(("title","blog"),)


class Article(models.Model):
    """
    文章
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, verbose_name="文章标题",blank=False)  # 文章标题
    desc = models.TextField(verbose_name="文章描述",max_length=500)  # 文章描述
    create_time = models.DateTimeField(auto_now_add=True)  # 创建时间
    content = RichTextUploadingField(verbose_name="文章内容",
                                     default='',
                                     null=True,
                                     blank=True,
                                     # CKEDITOR.config.extraPlugins:
                                     # config_name='my-custom-toolbar',
                                     extra_plugins=['codesnippet'],
                                     # CKEDITOR.plugins.addExternal(...)
                                     external_plugin_resources=[(
                                         'codesnippet',
                                         '/static/ckeditor5-build-classic/codesnippet/',
                                         'plugin.js',
                                     )],
                                     )
    # 评论数
    comment_count = models.IntegerField(verbose_name="评论数", default=0)
    # 点赞数
    up_count = models.IntegerField(verbose_name="点赞数", default=0)
    # 踩
    down_count = models.IntegerField(verbose_name="踩数", default=0)

    category = models.ForeignKey(verbose_name="分类",to="Category",  null=True,on_delete=models.SET_NULL)
    user = models.ForeignKey(to="myauth.MyUserInfo", to_field="nid",null=True,on_delete=models.SET_NULL)
    tags = models.ManyToManyField(  # 中介模型

        verbose_name="标签",
        to="Tag",
        through="Article2Tag",
        through_fields=("article", "tag"),  # 注意顺序！！！
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = verbose_name



# class ArticleDetail(models.Model):
#     """
#     文章详情表
#     """
#     nid = models.AutoField(primary_key=True)
#     content = models.TextField()
#     article = models.OneToOneField(to="Article", to_field="nid",null=True,on_delete=models.SET_NULL)
#
#     class Meta:
#         verbose_name = "文章详情"
#         verbose_name_plural = verbose_name




class Article2Tag(models.Model):
    """
    文章和标签的多对多关系表
    """
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(to="Article", to_field="nid",null=True,on_delete=models.SET_NULL)
    tag = models.ForeignKey(to="Tag", to_field="nid",null=True,on_delete=models.SET_NULL)

    class Meta:
        unique_together = (("article", "tag"),)
        verbose_name = "文章-标签对照"
        verbose_name_plural = verbose_name


class ArticleUpDown(models.Model):
    """
    点赞表
    """
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey(to="myauth.MyUserInfo", null=True,on_delete=models.SET_NULL)
    article = models.ForeignKey(to="Article", null=True,on_delete=models.SET_NULL)
    is_up = models.BooleanField(default=False)

    class Meta:
        unique_together = (("article", "user"),)
        verbose_name = "文章点赞"
        verbose_name_plural = verbose_name


class Comment(models.Model):
    """
    评论表
    """
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(to="Article", to_field="nid",null=True,on_delete=models.SET_NULL)
    user = models.ForeignKey(to="myauth.MyUserInfo", to_field="nid",null=True,on_delete=models.SET_NULL)
    content = RichTextUploadingField(verbose_name="评论内容",
                                     default='',
                                     null=False,
                                     blank=False,
                                     config_name='my-custom-toolbar',
                                     extra_plugins=['codesnippet'],
                                     external_plugin_resources=[(
                                         'codesnippet',
                                         '/static/ckeditor5-build-classic/codesnippet/',
                                         'plugin.js',
                                     )],
                                     )
    create_time = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey("self", null=True, blank=True,on_delete=models.SET_NULL)  # blank=True 在django admin里面可以不填

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = verbose_name