from django.http import JsonResponse
from django.shortcuts import render

from bug_app.forms.issues_form import IssuesForm
from bug_app.models import Issues
from bug_app.utils.pagination import Pagination


def issue_view(request,project_id):

    query={}
    issue_list = Issues.objects.all(**query)
    page_obj = Pagination(issue_list, request)
    page_queryset = page_obj.page_queryset
    page_string = page_obj.generate_pagination_html()
    return render(request,'platform/issue/issue.html',{'issues':page_queryset,'page_string':page_string})

def issue_add_view(request,project_id):
    if request.method=='POST':
        data_dict={}
        form = IssuesForm(request.POST,request=request)
        if form.is_valid():
            form.instance.creator=request.tracer.user
            form.instance.project=request.tracer.project
            form.save()
            data_dict['status'] = True
        else:
            data_dict['status'] = False
            data_dict['Error'] = form.errors
        return JsonResponse(data_dict)

    form = IssuesForm(request=request)
    return render(request,'platform/issue/issue_add.html',{'form':form})