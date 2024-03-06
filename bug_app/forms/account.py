import re

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django_redis import get_redis_connection

from bug_app.models import UserInfo
from bug_app.utils import sms_code,encrypt


#样式继承
class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BootstrapModelForm, self).__init__(*args, **kwargs)
        #循环找到所有的字段，并将他们的插件添加class
        for name,field in self.fields.items():
            if field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] ='请输入 %s' % (field.label,)
            else:
                field.widget.attrs = {'class':'form-control'}
class BootstrapForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BootstrapForm, self).__init__(*args, **kwargs)
        #循环找到所有的字段，并将他们的插件添加class
        for name,field in self.fields.items():
            if field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = '请输入 %s' % (field.label,)
            else:
                field.widget.attrs = {'class':'form-control'}

#用户注册
class UserRegForm(BootstrapModelForm):
    #验证码
    captcha = forms.CharField(widget=forms.TextInput,label="手机验证码")
    #确认密码
    confirm_password = forms.CharField(widget=forms.PasswordInput(render_value=True), label="确认密码"
                                       )  # 二次输入
    class Meta:
        model = UserInfo
        fields = ['username', 'email','password','confirm_password','mobile_phone','captcha']

    #检测是否注册过
    def clean_username(self):
        username = self.cleaned_data['username']
        exits = UserInfo.objects.filter(username=username).exists()
        if exits:
            raise ValidationError("用户名已经存在")
        return username
    def clean_email(self):
        email = self.cleaned_data['email']
        exits = UserInfo.objects.filter(email=email).exists()
        if exits :
            raise ValidationError('邮箱已经注册过')
        return email
    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        exits = UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exits:
            raise ValidationError('手机号已经注册')
        return mobile_phone

    #密码处理 + 加密
    def clean_password(self):
        password = self.cleaned_data['password']
        # 检查密码长度
        if len(password) < 8:
            raise ValidationError('密码不能小于8位')
        # 检查密码是否包含字母、数字和特殊符号
        if not re.search(r'[a-zA-Z]', password) or not re.search(r'\d', password) or not re.search(r'[\W_]', password):
            raise ValidationError('密码必须包含字母、数字和特殊符号')
        # 对密码进行加密
        cypto_pass = encrypt.toMd5(password)
        return cypto_pass
    def clean_confirm_password(self):
        confirm_password = self.cleaned_data['confirm_password']
        cypto_pass = encrypt.toMd5(confirm_password)
        if cypto_pass != self.cleaned_data['password']:# password已经先一步钩子函数换成md5了
            raise ValidationError("和第一次输入密码不匹配")
        return confirm_password

    #检测手机验证码
    def clean_captcha(self):
        code = self.cleaned_data['captcha']
        conn = get_redis_connection('default')
        mobile_phone = self.cleaned_data.get('mobile_phone')
        if not mobile_phone:
            return code

        print(mobile_phone)
        redis_code = conn.get('reg_code'+mobile_phone)
        if not redis_code:
            raise ValidationError("验证码已经失效或无")
        redis_code=redis_code.decode('utf-8')
        if redis_code != code:
            raise ValidationError("验证码错误")
        return code

class UserLoginForm(BootstrapModelForm):
    captcha = forms.CharField(widget=forms.TextInput,label="验证码")
    confirm_password = forms.CharField(widget=forms.PasswordInput(render_value=True), label="确认密码")  # 二次输入
    class Meta:
        model = UserInfo
        fields = ['username', 'password','confirm_password','captcha']


# 短信验证码Form
class SendSmsForm(BootstrapForm):
    mobile_phone = forms.CharField(label="手机号",
                            validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$','手机格式错误')])
    def clean_mobile_phone(self):
        #手机号校验
        mobile_phone = self.cleaned_data['mobile_phone']
        exits = UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exits:
            raise ValidationError("手机号已经存在")

        # 手机号校验
        code = sms_code.generate_sms_code()
        sres = sms_code.send_sms(code, mobile_phone)
        if sres is not True:
            raise ValidationError(sres)
        # redis写入
        conn = get_redis_connection('default')
        conn.set('reg_code'+mobile_phone, code,ex=60)

        return mobile_phone
