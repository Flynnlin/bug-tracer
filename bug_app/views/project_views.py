from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from bug_app.forms.project import ProjectModelform
from bug_app.models import Project,ProjectUser


def project_list_view(request):
    # 从中间件获取当前用户
    current_user=request.tracer.user

    # 创建
    if request.method == 'POST': #如果时post 则是获取新建项目数据
        rep_msg={}
        form=ProjectModelform(request.POST,request=request)
        if form.is_valid():

            form.instance.creator=current_user
            form.save()

            rep_msg['status'] = True
        else:
            rep_msg['status'] = False
            rep_msg['errors']=form.errors
        return JsonResponse(rep_msg)

    # 显示页面-展示项目
    if request.method == 'GET':
        form = ProjectModelform() #项目创建的form

        # 创建的项目
        user_created_projects=Project.objects.filter(creator=current_user)
        # 参与的项目 https://www.bilibili.com/video/BV1uA411b77M/?p=90&spm_id_from=pageDriver&vd_source=68cccc92a666a110c3d4162f94963373
        user_joined_projects = ProjectUser.objects.filter(user=current_user)
        # 设置是三个列表 收藏、创建、参加
        project_dict={'star':[],'created':[],'joined':[]}
        for project in user_created_projects:
            project_dict['star' if project.star else 'created'].append(project)
        for project in user_joined_projects:
            project_dict['star' if project.star else 'joined'].append(project.project)

        return render(request,'platform/project_list.html',{'form':form,'project_dict':project_dict})


# 定义视图函数project_star_view，接受request、project_type和project_id参数
def project_star_view(request, project_type, project_id):
    # 获取当前用户
    current_user = request.tracer.user

    # 如果project_type为'my'，表示操作的是当前用户创建的项目
    if project_type == 'my':
        # 根据项目id和当前用户筛选项目并将star字段更新为True
        Project.objects.filter(id=project_id, creator=current_user).update(star=True)
        # 重定向到项目列表页面
        return redirect('/project/list')

    # 如果project_type为'join'，表示操作的是当前用户加入的项目
    elif project_type == 'join':
        # 根据项目id和当前用户筛选ProjectUser对象并将star字段更新为True
        ProjectUser.objects.filter(project_id=project_id, user=current_user).update(star=True)
        # 重定向到项目列表页面
        return redirect('/project/list')

    # 如果project_type为'stared'，表示操作的是当前用户已经收藏的项目
    elif project_type == 'stared':
        # 如果当前用户是项目的创建者
        if Project.objects.filter(creator=current_user, id=project_id).exists():
            # 根据项目id和当前用户筛选项目并将star字段更新为False
            Project.objects.filter(creator=current_user, id=project_id).update(star=False)
        else:
            # 否则，当前用户是项目的成员，根据项目id和当前用户筛选ProjectUser对象并将star字段更新为False
            ProjectUser.objects.filter(project_id=project_id, user=current_user).update(star=False)
        # 重定向到项目列表页面
        return redirect('/project/list')

    # 如果project_type不是上述三种情况，则返回错误响应
    else:
        return HttpResponse('错误')