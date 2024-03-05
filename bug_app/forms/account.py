
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from bug_app.models import UserInfo


#样式继承
class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BootstrapModelForm, self).__init__(*args, **kwargs)
        #循环找到所有的字段，并将他们的插件添加class
        for name,field in self.fields.items():
            if field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs = {'class':'form-control'}
class BootstrapForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BootstrapForm, self).__init__(*args, **kwargs)
        #循环找到所有的字段，并将他们的插件添加class
        for name,field in self.fields.items():
            if field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
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

class UserLoginForm(BootstrapModelForm):
    captcha = forms.CharField(widget=forms.TextInput,label="验证码")
    confirm_password = forms.CharField(widget=forms.PasswordInput(render_value=True), label="确认密码")  # 二次输入
    class Meta:
        model = UserInfo
        fields = ['username', 'password','confirm_password','captcha']

class SendSmsForm(BootstrapForm):
    mobile_phone = forms.CharField(label="手机号",
                            validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$','手机格式错误')])


    def clean_phone(self):
        #手机号校验
        mobile_phone = self.cleaned_data['mobile_phone']
        exits = UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exits:
            raise ValidationError("手机号已经存在")
        return mobile_phone
