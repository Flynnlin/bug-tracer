
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from bug_app.models import UserInfo


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 获取用户信息
        user_info = request.session.get("user_info", None)

        # 页面白名单，login页面不需要鉴权
        allowed_url = [
            "/send/sms/",
            "/send/logincode/",
            "/user/login/sms/",
            "/user/login/",
            "/user/reg/",
            "/index/",
        ]

        # 如果请求路径在白名单中，则不需要鉴权
        if request.path_info in allowed_url:
            if user_info is not None:
                # 获取用户对象
                # 为了在后续的请求处理中能够使用该用户对象的信息，比如用户的权限、个人设置等。
                user_obj = UserInfo.objects.filter(id=user_info['user_id']).first()
                request.tracer = user_obj
            return  # 通过

        # 如果用户未登录，则重定向到登录页面
        if user_info is None:
            return redirect('/user/login/sms/')  # 未登录不通过
