import base64

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from bug_app.models import UserInfo
from bug_app.forms.account import UserRegForm, UserLogin_SMS_Form, SendSmsForm, UserLogin_code_Form

from django_redis import get_redis_connection
from django.views.decorators.csrf import csrf_exempt

from bug_app.utils import captcha

"""# 用户账户  注册 登录 注销"""


# 注册
def user_register_view(request):
    if request.method == 'POST':
        form = UserRegForm(request.POST)
        response_msg = {}
        if form.is_valid():  # 数据校验
            form.save()  # 会自动剔除数据模型中没有的字段
            response_msg['status'] = True
            response_msg['reload'] = '/user/login/sms/'
        else:
            response_msg['Error'] = form.errors
        return JsonResponse(response_msg)

    Form = UserRegForm()
    return render(request, 'account/SMS_register.html',
                  {'form': Form})


# 登录1
def user_SMSlogin_view(request):
    if request.method == 'POST':
        form = UserLogin_SMS_Form(request.POST)
        response_msg = {}
        if form.is_valid():
            # 如果验证通过，phone钩子函数直接返回的用户对象
            user_obj=form.cleaned_data['mobile_phone']
            response_msg['status'] = True
            response_msg['reload'] = '/index/'

            # 添加登录凭证
            user_info={
                'username': user_obj.username,
                'user_id': user_obj.id
            }
            request.session['user_info'] = user_info
            request.session.set_expiry(7200)  # 设置超时时间

        else:
            response_msg['Error'] = form.errors
        return JsonResponse(response_msg)

    Form = UserLogin_SMS_Form()
    return render(request, 'account/SMS_login.html',
                  {'form': Form})

# 登录2
def user_login_view(request):

    if request.method == 'POST':
        form = UserLogin_code_Form(request.POST)
        success,userF, user_obj = form.user_login(request)
        print(success)
        if success:
            # 添加登录凭证
            user_info = {
                'username': user_obj.username,
                'user_id': user_obj.id
            }
            request.session['user_info'] = user_info
            request.session.set_expiry(7200)  # 设置超时时间
            return redirect('/index/')
        else:
            print(userF.errors)
            return render(request, 'account/picCode_Login.html',
                          {'form': userF, 'code_img_io': request.session.get('code_img_io')})


    img_code_view(request)

    Form = UserLogin_code_Form
    return render(request,'account/picCode_Login.html',
                  {'form': Form,'code_img_io':request.session.get('code_img_io')})



def user_logout(request):
    request.session.clear()
    return redirect('/user/login/')


# 生成图片验证码和设置
def img_code_view(request):
    #图片验证码生成 每次访问都刷新
    captcha_text, img_io=captcha.generate_captcha()
    img_io_base64 = base64.b64encode(img_io.getvalue()).decode()
    request.session['code_txt'] = captcha_text  # 保存当次验证码
    request.session['code_img_io'] = img_io_base64
    request.session.set_expiry(60)  # 设置超时时间

    return HttpResponse(img_io_base64)
# 发送验证码
@csrf_exempt
def send_sms_view(request):
    msg = {}
    phoneForm = SendSmsForm(data=request.POST)
    # 手机号校验&手机号校验&redis写入临时验证码
    if phoneForm.is_valid():
        msg['status'] = True
    else:
        msg['Error'] = phoneForm.errors
    return JsonResponse(msg)
