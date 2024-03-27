from django import forms


from bug_app.forms.BootStrapForm import BootstrapModelForm
from bug_app.models import Issues, UserInfo, Module, IssuesType, ProjectUser, Project, IssuesReply


class IssuesForm(BootstrapModelForm):
    class Meta:
        model = Issues
        fields = '__all__'
        exclude = ['create_datetime', 'latest_update_datetime','creator','project']
        widgets={
            "assign":forms.Select(attrs={'class':'form-control singleSelect'}),
            "attention":forms.SelectMultiple(attrs={'class':'form-control singleSelect'}),
            "parent":forms.Select(attrs={'class':'form-control singleSelect'}),
        }
    def __init__(self, *args, **kwargs):
        super(IssuesForm, self).__init__(*args, **kwargs)
        #1.指派者和关注者必须是本项目的人
        all_users = [(self.request.tracer.project.creator.id, self.request.tracer.project.creator.username)]
        all_users.extend(
            ProjectUser.objects.filter(project=self.request.tracer.project).values_list('user_id', 'user__username'))
        self.fields['assign'].choices =[("","不分配到人物")]+ all_users
        self.fields['attention'].choices = all_users
        #2.父问题必须是本项目的
        self.fields['parent'].queryset = Issues.objects.filter(project=self.request.tracer.project)
        #3 .项目进度也是当前项目的
        self.fields['module'].queryset = Module.objects.filter(project=self.request.tracer.project)
        #4 .项目类型也是当前项目的
        self.fields['issues_type'].queryset = IssuesType.objects.filter(project=self.request.tracer.project)

class IssuesReplyModelForm(BootstrapModelForm):
    class Meta:
        model = IssuesReply
        fields = ['content', 'reply']