from datetime import datetime

from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from bug_app.models import UserInfo, Transaction, Project, ProjectUser


class Tracer(object):
    def __init__(self):
        self.user = None
        self.price_policy=None
        self.project = None

class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.tracer = Tracer()
        # 获取用户信息
        user_info = request.session.get("user_info", None)
        if user_info is not None:
            # 获取用户对象
            # 为了在后续的请求处理中能够使用该用户对象的信息，比如用户的权限、个人设置等。
            user_obj = UserInfo.objects.filter(id=user_info['user_id']).first()
            request.tracer.user = user_obj

            # 获取用户最新的价格策略
            # s1 查交易记录 获取当前用户最新的交易记录信息
            user_newtra=Transaction.objects.filter(user=user_obj,status=2).order_by('-id').first()
            # s2 判读是否过期
            if user_newtra.end_datetime and user_newtra.end_datetime < datetime.now():#过期
                #过期则使用免费版策略
                user_newtra = Transaction.objects.filter(user=user_obj, status=2,price_policy__category=1).first()
            request.tracer.price_policy = user_newtra.price_policy

            # 获取当前用户的项目信息
            # 创建的项目
            user_created_projects = Project.objects.filter(creator=user_obj)
            # 参与的项目
            user_joined_projects = ProjectUser.objects.filter(user=user_obj)
            request.tracer.created_projects = user_created_projects
            request.tracer.joined_projects = user_joined_projects

        # 页面白名单，login页面不需要鉴权
        allowed_url = [
            "/send/sms/",
            "/send/logincode/",
            "/user/login/sms/",
            "/user/login/",
            "/user/timeout/",
            "/user/reg/",
            "/"
        ]

        # 如果请求路径在白名单中，则不需要鉴权
        if request.path_info in allowed_url or 'index' in request.path_info:
            return  # 通过

        # 如果用户未登录，则重定向到登录页面
        if user_info is None:
            return redirect('/user/timeout/')  # 未登录不通过



# 进入项目管理页面的中间件
class AuthMiddleware2(MiddlewareMixin):
    def process_request(self, request):
        path = request.path
        user = request.tracer.user
        project_id = None
        if path == '/mdeditor/uploads/':
            referer = request.headers.get('Referer')
            if referer:
                referer_path = referer.split(request.get_host())[1]
                project_id = referer_path.split('/')[2]  # 提取项目ID
        if (path.startswith('/project/') and '/dashboard/' in path):
            # 进行权限检查
            project_id = path.split('/')[2]  # 提取项目ID
        if project_id is not None:
            # 判断是否有进入的权限（要求用户创建的或者参与的）
            access = (Project.objects.filter(id=project_id, creator=user).exists()
                      or ProjectUser.objects.filter(project_id=project_id, user=user).exists())
            if not access:
                return HttpResponseForbidden("""<!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Permission Denied</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f8f9fa;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
    
        .container {
            text-align: center;
        }
    
        h1 {
            color: #dc3545;
            font-size: 24px;
            margin-bottom: 20px;
        }
    
        p {
            color: #6c757d;
            font-size: 16px;
        }
    </style>
    </head>
    <body>
    <div class="container">
        <h1>Permission Denied</h1>
        <p>You don't have permission to access this project.</p>
    </div>
    </body>
    </html>
    """)
            else:
                request.tracer.project = Project.objects.get(id=project_id)
            return  # 通过


# class AuthMiddleware2(MiddlewareMixin):
#     def process_request(self, request):
#         path = request.path
#         if path.startswith('/project/') and '/dashboard/' in path:
#             user=request.tracer.user
#             # 进行权限检查
#             project_id = path.split('/')[2]  # 提取项目ID
#
#             #判断是否有进入的权限（要求用户创建的或者参与的）
#             access = (Project.objects.filter(id=project_id,creator=user).exists()
#                       or ProjectUser.objects.filter(project_id=project_id,user=user).exists())
#             if not access:
#                 return HttpResponseForbidden("""<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Permission Denied</title>
#     <style>
#         body {
#             font-family: Arial, sans-serif;
#             background-color: #f8f9fa;
#             margin: 0;
#             padding: 0;
#             display: flex;
#             justify-content: center;
#             align-items: center;
#             height: 100vh;
#         }
#
#         .container {
#             text-align: center;
#         }
#
#         h1 {
#             color: #dc3545;
#             font-size: 24px;
#             margin-bottom: 20px;
#         }
#
#         p {
#             color: #6c757d;
#             font-size: 16px;
#         }
#     </style>
# </head>
# <body>
#     <div class="container">
#         <h1>Permission Denied</h1>
#         <p>You don't have permission to access this project.</p>
#     </div>
# </body>
# </html>
# """)
#             else:
#                 request.tracer.project=Project.objects.get(id=project_id)
#             return  # 通过