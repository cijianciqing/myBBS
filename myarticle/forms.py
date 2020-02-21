from django import forms
from django.forms import widgets
from ckeditor_uploader.fields import RichTextUploadingFormField


from myarticle import models
# class CreateArticleForm(forms.Form):
#     # 重写父类的init方法
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields["tags"].widget.choices=models.Tag.objects.all().values_list("nid", "title"),
#         self.fields["category"].widget.choices=models.Category.objects.all().values_list("nid", "title"),
#
#
#         # filter(blog=currentUser.blog)
#
#     title = forms.CharField(
#         # 校验规则相关
#         min_length=6,
#         max_length=16,
#         label="文章标题",
#         error_messages={
#             "required": "该字段不能为空",
#             "min_length": "用户名最少6位！",
#         },
#         # widget控制的是生成html代码相关的
#         widget=widgets.TextInput(attrs={"class": "form-control"})
#     )
#
#     category = forms.ChoiceField(
#         choices=(),
#         label="分类",
#         initial=1,
#         widget=forms.widgets.Select(attrs={"class": "form-control"})
#     )
#
#     tags = forms.MultipleChoiceField(
#         choices=(),
#         label="标签",
#         initial=1,
#         widget=forms.widgets.SelectMultiple(attrs={"class": "form-control"})
#     )
#
#     content = RichTextUploadingFormField(label="标签",config_name="my-custom-toolbar")

class CreateArticleForm(forms.ModelForm):
    # 重写父类的init方法,获取当前用户自己的tags
    def __init__(self,is_update,currentUser, *args, **kwargs):
        # print('this is init method in CreateArticleForm')
        super().__init__(*args, **kwargs)
        self.is_update = is_update
        self.fields["category"].widget.choices = models.Category.objects.all().values_list('nid', 'title')
        self.fields['category'].widget.attrs.update({'class': 'form-control'})

        self.fields["tags"].widget.choices = models.Tag.objects.filter(blog=currentUser.blog).values_list('nid','title')
        self.fields['tags'].widget.attrs.update({'class': 'form-control'})

        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['desc'].widget.attrs.update({'class': 'form-control'})


    class Meta:
        fields = ['title','desc', 'content', 'category', 'tags']  # 引入全部字段
        model = models.Article
        error_messages = {
            'title': {
                'required': '字段不能为空ya',
                'max_length': "超过最大长度了ya",
            },
        }

class CommentForm(forms.ModelForm):
    # 重写父类的init方法,获取当前用户自己的tags
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['content'].widget.attrs.update({'cols':60, 'rows':10})
    #     # print('this is init method in CreateArticleForm')
    #     super().__init__(*args, **kwargs)
    #     self.fields["category"].widget.choices = models.Category.objects.all().values_list('nid', 'title')
    #     self.fields['category'].widget.attrs.update({'class': 'form-control'})
    #
    #     self.fields["tags"].widget.choices = models.Tag.objects.filter(blog=currentUser.blog).values_list('nid','title')
    #     self.fields['tags'].widget.attrs.update({'class': 'form-control'})
    #
    #     self.fields['title'].widget.attrs.update({'class': 'form-control'})
    #     self.fields['desc'].widget.attrs.update({'class': 'form-control'})
    class Meta:
        model = models.Comment
        fields = ['content']  # 引入全部字段
        # widgets = {
        #     'content': RichTextUploadingFormField( attrs= {'cols':60, 'rows':10}),
        # }
        # error_messages = {
        #     'title': {
        #         'required': '字段不能为空ya',
        #         'max_length': "超过最大长度了ya",
        #     },
        # }



