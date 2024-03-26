import base64
import datetime
import re

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django_redis import get_redis_connection

from bug_app.forms.account_form import UserRegForm, UserLogin_SMS_Form, SendSmsForm, UserLogin_code_Form
from bug_app.utils import captcha, uuidStr, encrypt
from bug_app.models import Transaction, PricePolicy

"""
用户账户  注册 登录 注销
相关实现
用户信息展示（基本信息和账单）
"""


# 注册
def user_register_view(request):
    if request.method == 'POST':
        form = UserRegForm(request.POST)
        response_msg = {}
        if form.is_valid():  # 数据校验

            instance = form.save()  # 会自动剔除数据模型中没有的字段

            # 创建交易记录-（免费用户）
            price_policy = PricePolicy.objects.get(category=1, title="个人免费版")
            Transaction.objects.create(
                status=2,
                order=uuidStr.generate_order_number(),
                user=instance,
                price_policy=price_policy,
                count = 0,
                price = 0,
                start_datetime=datetime.datetime.now()
            )

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
            user_obj = form.cleaned_data['mobile_phone']
            response_msg['status'] = True
            response_msg['reload'] = '/index/'

            # 添加登录凭证
            user_info = {
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
        success, userF, user_obj = form.user_login(request)
        print(success)
        if success:
            # 添加登录凭证
            user_info = {
                'username': user_obj.username,
                'user_id': user_obj.id
            }
            request.session['user_info'] = user_info
            request.session.set_expiry(86400 * 3)  # 设置会话过期时间为一天（86400 秒）
            return redirect('/index/')
        else:
            print(userF.errors)
            return render(request, 'account/picCode_Login.html',
                          {'form': userF, 'code_img_io': request.session.get('code_img_io')})

    img_code_view(request)

    Form = UserLogin_code_Form
    return render(request, 'account/picCode_Login.html',
                  {'form': Form, 'code_img_io': request.session.get('code_img_io')})


# 注销
def user_logout(request):
    request.session.clear()
    return redirect('/index/')


# 登录过期提示
def login_timeout_view(request):
    return render(request, 'account/loginTimeout.html')

# 生成图片验证码和设置
def img_code_view(request):
    # 图片验证码生成 每次访问都刷新
    captcha_text, img_io = captcha.generate_captcha()
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


def user_info_view(request):
    # 用户信息
    # 账单
    transaction = Transaction.objects.filter(user=request.tracer.user).order_by('-id')
    return render(request,'account/my_info.html',{'transaction':transaction})


def user_change_password_view(request):
    if request.method == 'POST':
        newPass=request.POST.get('newPass')
        code = request.POST.get('code')
        conn = get_redis_connection('default')
        redis_code = conn.get('sms_code' + request.tracer.user.mobile_phone)
        redis_code = redis_code.decode('utf-8')
        if len(newPass) < 8:
            return HttpResponse('密码不能小于8位')
        # 检查密码是否包含字母、数字和特殊符号
        if not re.search(r'[a-zA-Z]', newPass) or not re.search(r'\d', newPass) or not re.search(r'[\W_]', newPass):
            return HttpResponse('密码必须包含字母、数字和特殊符号')
        # 对密码进行加密
        cypto_pass = encrypt.toMd5(newPass)
        print(redis_code)
        if code == redis_code: #验证通过
            request.tracer.user.password = cypto_pass
            request.tracer.user.save()
            request.session.clear()
            return redirect('/index/')
        return HttpResponse('失败')