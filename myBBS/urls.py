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

from myarticle import views

# handler404 = 'myauth.views.my_custom_page_not_found_view'

urlpatterns = [
    # ckeditor图片上传
    # path('ckeditor/', include('ckeditor_uploader.urls')),
    path('ckeditor/', include('myarticle.utils.urls')),
    re_path(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico')),
    re_path(r'^media/(?P<path>.*)$', static.serve, kwargs={'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', static.serve, kwargs={'document_root': settings.STATIC_ROOT}, name='static'),
    path('admin/', admin.site.urls),

    # path('', TemplateView.as_view(template_name="index.html")),
    path('', views.index,name='index'),

    path('1/', TemplateView.as_view(template_name="index2.html")),

    path('myAuth/', include('myauth.urls')),
    path('myBlog/', include('myarticle.urls')),
]
