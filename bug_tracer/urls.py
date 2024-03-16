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
from bug_app.views import userAccount_views, index_views, project_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # 网站首页
    path('',index_views.index_view,name='index'),
    path('index/',index_views.index_view,name='index'),
    path('index/doc/',index_views.index_doc_view,name='index_doc'),
    path('index/function/',index_views.index_function_view,name='index_function'),
    path('index/price/',index_views.index_price_view,name='index_price'),
    path('index/scheme/',index_views.index_scheme_view,name='index_scheme'),

    # 用户账户
    path('user/reg/', userAccount_views.user_register_view, name='user_register'),
    path('user/login/sms/', userAccount_views.user_SMSlogin_view, name='user_login_sms'),
    path('user/login/', userAccount_views.user_login_view, name='user_login'),
    path('user/logout/', userAccount_views.user_logout,name='user_logout'),
    path('send/sms/', userAccount_views.send_sms_view, name='sms_code'),
    path('send/logincode/', userAccount_views.img_code_view, name='send_img_code'),
    path('user/timeout/', userAccount_views.login_timeout_view, name='login_timeout'),

    #系统页面
    path('project/list/', project_views.project_list_view, name='project_list'),
    # 区分 project/star/my/1  project/star/join/1
    path('project/star/<str:project_type>/<int:project_id>/', project_views.project_star_view, name='project_star')

]
