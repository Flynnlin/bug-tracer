from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from bug_app.forms.project_form import ProjectModelform
from bug_app.models import Project
from bug_app.utils import oss
from django.views.decorators.csrf import csrf_exempt

def project_setting_view(request,project_id):

    return render(request,'platform/setting/project_setting.html')


@csrf_exempt
def project_setting_delete(request,project_id):
    if request.method == 'POST':
        print(request.POST)
        project = Project.objects.get(id=project_id)
        confirm_name = request.POST.get('confirm_name')
        if confirm_name and confirm_name == project.name:
            bucket_name = project.bucket
            # 删除桶
            cloud = oss.ConnectOss()
            cloud.delete_folder(bucket_name,"fileRepository/")
            cloud.delete_folder(bucket_name,"wikieditor/")
            cloud.delete_bucket(bucket_name)
            # 删除项目
            Project.objects.filter(id=project_id).delete()
            return JsonResponse({'status':True})
        else:
            return JsonResponse({'status':False,'msg':'你不想删除吧'})


    return render(request,'platform/setting/project_setting_del.html')

def project_setting_edit(request,project_id):
    project = Project.objects.get(id=project_id)

    if request.method == 'POST':
        form = ProjectModelform(instance=project,data=request.POST,request=request)
        if form.is_valid():
            form.save()
            return redirect(reverse('project_settings',args=[project_id]))
        else:
            return render(request, 'platform/setting/project_setting_edit.html', {'form': form})


    form = ProjectModelform(instance=project,request=request)
    return render(request,'platform/setting/project_setting_edit.html',{'form':form})