from django.http import JsonResponse
from django.shortcuts import render, redirect
from bug_app.models import UserInfo
from bug_app.forms.account import UserRegForm,UserLoginForm,SendSmsForm


from django_redis import get_redis_connection
from django.views.decorators.csrf import csrf_exempt

"""# 用户账户  注册 登录 注销"""

#注册
def user_register_view(request):

    if request.method == 'POST':
        form = UserRegForm(request.POST)
        response_msg={}
        if form.is_valid():  #数据校验
            form.save()  #会自动剔除数据模型中没有的字段
            response_msg['status'] = True
            response_msg['reload'] = '/user/login/'
        else:
            response_msg['Error'] = form.errors
        return JsonResponse(response_msg)


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
    # 手机号校验&手机号校验&redis写入临时验证码
    if phoneForm.is_valid():
        msg['status'] = True
    else:
        msg['Error'] = phoneForm.errors
    return JsonResponse(msg)
