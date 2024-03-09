from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):

        # ## 页面排除，login页面不需要鉴权
        # if (request.path_info == "/user/login/sms/"
        #         or request.path_info == "/user/login/code/"
        #         or request.path_info == "/user/reg/"):
        #     return  #通过
        # if request.session.get('user_info')['username'] is None:
        #     return redirect('/user/login/sms/')  #不通过
        pass