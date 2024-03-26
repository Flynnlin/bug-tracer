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
from bug_app.views import userAccount_views, index_views, project_views, wiki_view, fileRepository_view, \
    project_setting_view, issue_view, statistics_views, pay_view

urlpatterns = [
    path('admin/', admin.site.urls),

    # 网站首页
    path('',index_views.index_view,name='index'),
    path('index/',index_views.index_view,name='index'),
    path('index/doc/',index_views.index_doc_view,name='index_doc'),
    path('index/function/',index_views.index_function_view,name='index_function'),
    path('index/price/',pay_view.show_pay_view,name='index_price'),
    path('index/scheme/',index_views.index_scheme_view,name='index_scheme'),

    # 支付页面
    path('user/payment/', pay_view.payment_view, name='payment_view'),
    path('user/pay/', pay_view.pay_view, name='pay_view'),
    path('user/pay/notify/', pay_view.pay_notify_view, name='pay_notify_view'),
    # 用户账户
    path('user/reg/', userAccount_views.user_register_view, name='user_register'),
    path('user/login/sms/', userAccount_views.user_SMSlogin_view, name='user_login_sms'),
    path('user/login/', userAccount_views.user_login_view, name='user_login'),
    path('user/logout/', userAccount_views.user_logout,name='user_logout'),
    path('send/sms/', userAccount_views.send_sms_view, name='sms_code'),
    path('send/logincode/', userAccount_views.img_code_view, name='send_img_code'),
    path('user/timeout/', userAccount_views.login_timeout_view, name='login_timeout'),
    path('user/info/', userAccount_views.user_info_view, name='user_info'),
    path('user/changePass/', userAccount_views.user_change_password_view,name='user_change_password_view'),

    #系统页面
    path('project/list/', project_views.project_list_view, name='project_list'),
    path('project/join/<int:code>/',project_setting_view.invite_join, name='invite_join'),
    # 区分 project/star/my/1  project/star/join/1
    path('project/star/<str:project_type>/<int:project_id>/', project_views.project_star_view, name='project_star'),

    #项目管理面板
    path('project/<int:project_id>/dashboard/', include(
        [
        path('', project_views.project_dashboard_view, name='project_dashboard'),
            path('wiki/', include([
                path('',wiki_view.project_wiki_list_view, name='project_wiki'),
                path('add/',wiki_view.project_wiki_add_view, name='project_wiki_add'),
                path('<int:wiki_id>/',wiki_view.project_wiki_detail_view, name='project_wiki_detail'),
                path('<int:wiki_id>/del/',wiki_view.project_wiki_del_view, name='project_wiki_del'),
                path('<int:wiki_id>/edit/',wiki_view.project_wiki_edit_view, name='project_wiki_edit'),
            ])),
            path('file/', include([
                path('', fileRepository_view.fileRepository_list_view, name='project_file'),
                path('upload/', fileRepository_view.fileRepository_upload_view, name='project_file_upload'),
                path('del/', fileRepository_view.fileRepository_delete_view, name='project_file_delete')
            ])),
        path('settings/', project_setting_view.project_setting_view, name='project_settings'),
        path('settings/del/', project_setting_view.project_setting_delete, name='project_settings_del'),
        path('settings/edit/', project_setting_view.project_setting_edit, name='project_settings_edit'),
        path('settings/invite/', project_setting_view.project_invite_view, name='project_invite'),
        path('settings/exit/', project_setting_view.project_settings_exit, name='project_settings_exit'),
        path('settings/custom/', project_setting_view.custom_project_view, name='project_settings_custom'),

        path('issues/', include([
            path('', issue_view.issue_view, name='issue'),
            path("add/", issue_view.issue_add_view, name='issue_add'),
            path("<int:issue_id>/",issue_view.issue_edit_view, name='issue_detail'),
            path("<int:issue_id>/getReply/",issue_view.issue_get_reply_view, name='issue_get_reply'),
        ])),
        path('statistics/', statistics_views.statistic_view, name='project_statistics'),
        path('statistics/api/getType', statistics_views.projectIssue_type_view,name='projectIssueType'),
        path('statistics/api/getStatus', statistics_views.projectUser_work_view,name='projectUserWork'),
        ])
    ),
    path('mdeditor/', include(('mdeditor.urls', 'mdeditor'), namespace='mdeditor')), # 配置编辑器路由
]
if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
