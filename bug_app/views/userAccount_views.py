from django.http import JsonResponse
from django.shortcuts import render
from bug_app.models import UserInfo
from bug_app.forms.account import UserRegForm,UserLoginForm,SendSmsForm

from bug_app.utils import sms_code
from django_redis import get_redis_connection
from django.views.decorators.csrf import csrf_exempt

# 用户账户  注册 登录 注销

#注册
def user_register_view(request):
    if request.method == 'POST':
        form = UserRegForm(request.POST)
        if form.is_valid():
            pass
    Form = UserRegForm()
    return render(request, 'account/register.html',
                  {'form':Form})

#登录
def user_login_view(request):
    Form=UserLoginForm()
    return render(request, 'account/login.html',
                  {'form':Form})

#发送验证码
@csrf_exempt
def send_sms_view(request):
    msg={}
    phoneForm=SendSmsForm(data=request.POST)
    print(request.POST)
    # 格式校验
    if phoneForm.is_valid():

        msg['status'] = 'success'
    else:
        msg['Error'] = phoneForm.errors
    return JsonResponse(msg)
