from bug_app.forms.BootStrapForm import BootstrapModelForm
from bug_app.models import Wiki
from mdeditor.fields import MDTextFormField

class WikiModelForm(BootstrapModelForm):
    class Meta:
        model = Wiki
        fields = '__all__'
        exclude = ['project', 'depth']
    def __init__(self, *args, **kwargs):
        super(WikiModelForm, self).__init__(*args, **kwargs)
        self.fields['parent'].queryset = Wiki.objects.filter(project=self.request.tracer.project)
