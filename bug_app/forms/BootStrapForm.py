
from django import forms

#样式继承
class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
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
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        #循环找到所有的字段，并将他们的插件添加class
        for name,field in self.fields.items():
            if field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = '请输入 %s' % (field.label,)
            else:
                field.widget.attrs = {'class':'form-control'}