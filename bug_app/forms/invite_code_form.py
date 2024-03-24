from django import forms


from bug_app.forms.BootStrapForm import BootstrapModelForm
from bug_app.models import ProjectInvite


class InviteForm(BootstrapModelForm):
    class Meta:
        model = ProjectInvite
        fields = ['period', 'count']