
from django import forms
from django.core.exceptions import ValidationError
from bug_app.models import Project
from bug_app.forms.BootStrapForm import BootstrapForm, BootstrapModelForm


# 自定义插件样式用于 项目创建form的颜色选择
class ColorRadioSelect(forms.RadioSelect):
    template_name = "layout/color_radio_select.html"


# 创建项目form
class ProjectModelform(BootstrapModelForm):
    class Meta:
        model = Project
        fields = ['name', 'color', 'desc']
        widgets = {
            "desc": forms.Textarea(attrs={'class': 'form-control'}),
            "color": ColorRadioSelect()
            # ....
        }

    def clean_name(self):
        # 判读当前用户是否创建重复项目
        name = self.cleaned_data['name']
        Exisit = Project.objects.filter(name=name, creator=self.request.tracer.user).exists()
        if Exisit:  # 存在
            raise ValidationError("名字重复啦")

        # 判读是否还有创建项目余额
        project_max_num = self.request.tracer.price_policy.project_num
        project_current_num = Project.objects.filter(creator=self.request.tracer.user).count()
        if project_current_num >= project_max_num:
            raise ValidationError("已经创建了太多了项目了，购买套餐吧")

        # 全部限制通过
        return name
