from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib import auth
# from geetest import GeetestLib
from myauth import forms, models
from utils.myResponse import ReturnCode,wrap_json_response,CommonResponseMixin
from myBBS import settings
from myarticle.models import Blog
# Create your views here.

#自定义404错误处理视图
# def my_custom_page_not_found_view(request,exception):
#     return render(request,"my404.html")

# 注册的视图函数
def register(request):
    if request.method == "POST":
        print(request.get_full_path())
        form_obj = forms.RegForm(request.POST)
        # 帮我做校验
        if form_obj.is_valid():
            # 校验通过，去数据库创建一个新的用户
            form_obj.cleaned_data.pop("re_password")
            # 判断是否需要使用avatar的默认值【model默认值的使用规则】
            myuser=None
            if request.FILES.get("avatar"):
                avatar_img = request.FILES.get("avatar")
                myuser = models.MyUserInfo.objects.create_user(**form_obj.cleaned_data, avatar=avatar_img)
            else:
                myuser = models.MyUserInfo.objects.create_user(**form_obj.cleaned_data)

            blog =  Blog.objects.create(title=myuser.username)
            myuser.blog = blog
            myuser.save()
            # 注册成功后，跳转到登陆页面
            myResponseData = wrap_json_response(code = ReturnCode.SUCCESS ,message=settings.LOGIN_URL)
        else:
            myResponseData = wrap_json_response(data=form_obj.errors,code=ReturnCode.FAILED)
        return JsonResponse(data=myResponseData)
    # 生成一个form对象
    form_obj = forms.RegForm()
    return render(request, "myauth/myRegister.html", {"form_obj": form_obj})

# 登陆
def login(request):
    if request.method=="GET":
        if request.GET.get("next") != None:
            next_url = request.GET.get("next")
            request.session['afterLoginURL'] = next_url
            print("url_next: ",next_url)
        print("@!" * 100)
        print(request.get_full_path())
        # print(next_url)
        print("@!" * 100)
        # 在session中设置需要重定向的url
        return render(request,"myauth/myLogin.html",context={"loginError": False})
    # 处理login的Post请求
    #从session中获取重定向地址
    my_next_url="/"
    if request.session.get('afterLoginURL',None) != None :
        my_next_url = request.session['afterLoginURL']
    username = request.POST["inputEmail"]
    password = request.POST["inputPassword"]
    user_obj = auth.authenticate(username= username, password=password)
    # 登陆成功处理
    if user_obj:
        # 该函数实现一个用户登录的功能。它本质上会在后端为该用户生成相关session数据
        auth.login(request, user_obj)
        return redirect(my_next_url)
    # 登陆失败处理
    return render(request,"myauth/myLogin.html",context={"loginError": True})


def logout(request):
    auth.logout(request)
    return redirect(to="/")