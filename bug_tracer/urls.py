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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from bug_app.views import userAccount_views, index_views, project_views,wiki_view

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
    path('project/star/<str:project_type>/<int:project_id>/', project_views.project_star_view, name='project_star'),

    #项目管理面板
    path('project/<int:project_id>/dashboard/', include(
        [
        path('', project_views.project_dashboard_view, name='project_dashboard'),
        # path('issues/', project_views.project_issues_view, name='project_issues'),
        # path('statistics/', project_views.project_statistics_view, name='project_statistics'),
        # path('file/', project_views.project_file_view, name='project_file'),
        path('wiki/', include([
            path('',wiki_view.project_wiki_list_view, name='project_wiki'),
            path('add/',wiki_view.project_wiki_add_view, name='project_wiki_add'),
            path('<int:wiki_id>/',wiki_view.project_wiki_detail_view, name='project_wiki_detail'),
            path('<int:wiki_id>/del/',wiki_view.project_wiki_del_view, name='project_wiki_del'),
            path('<int:wiki_id>/edit/',wiki_view.project_wiki_edit_view, name='project_wiki_edit'),

        ])),
        # path('settings/', project_views.project_settings_view, name='project_settings'),
        ])
    ),
    path('mdeditor/', include(('mdeditor.urls', 'mdeditor'), namespace='mdeditor')), # 配置编辑器路由
]
if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
