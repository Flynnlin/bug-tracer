"""
URL configuration for bug_tracer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from bug_app.views import userAccount_views,index_views

urlpatterns = [
    # 网站首页
    path('index/',index_views.index_view,name='index'),
    # 用户账户
    path('user/reg/', userAccount_views.user_register_view, name='user_register'),
    path('user/login/sms/', userAccount_views.user_SMSlogin_view, name='user_login_sms'),
    path('user/login/', userAccount_views.user_login_view, name='user_login'),
    path('user/logout/', userAccount_views.user_logout,name='user_logout'),
    path('send/sms/', userAccount_views.send_sms_view, name='sms_code'),
    path('send/logincode/', userAccount_views.img_code_view, name='send_img_code'),

    #系统页面

]
