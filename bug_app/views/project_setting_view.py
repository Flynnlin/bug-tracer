import datetime
import random

from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from bug_app.forms.invite_code_form import InviteForm
from bug_app.forms.project_form import ProjectModelform
from bug_app.models import Project, ProjectInvite, ProjectUser, Transaction, PricePolicy
from bug_app.utils import oss
from django.views.decorators.csrf import csrf_exempt

"""
项目删除
项目信息更新
项目邀请
"""
def project_setting_view(request,project_id):

    return render(request,'platform/setting/project_setting.html')


@csrf_exempt
def project_setting_delete(request,project_id):
    if request.tracer.user != request.tracer.project.creator:
        Emsg = "没有权限查看，请联系项目创建者"
        return render(request, 'platform/setting/project_setting_del.html',{'Emsg':Emsg})
    if request.method == 'POST':
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
    if request.tracer.user != request.tracer.project.creator:
        Emsg = "没有权限查看，请联系项目创建者"
        return render(request, 'platform/setting/project_setting_edit.html',{'Emsg':Emsg})
    if request.method == 'POST':
        form = ProjectModelform(instance=project,data=request.POST,request=request)
        if form.is_valid():
            form.save()
            return redirect(reverse('project_settings',args=[project_id]))
        else:
            return render(request, 'platform/setting/project_setting_edit.html', {'form': form})


    form = ProjectModelform(instance=project,request=request)
    return render(request,'platform/setting/project_setting_edit.html',{'form':form})

@csrf_exempt
def project_settings_exit(request,project_id):
    project = Project.objects.get(id=project_id)
    if request.tracer.user == request.tracer.project.creator:
        Emsg = "项目创建者不能退出项目"
        return render(request, 'platform/setting/project_setting_exit.html', {'Emsg': Emsg})
    if request.method == 'POST':
        confirm_name = request.POST.get('confirm_name')
        if confirm_name and confirm_name == project.name:
            # 删除ProjectUser记录
            ProjectUser.objects.filter(project=project,user=request.tracer.user).delete()
            # project 人数-1
            project.join_count=project.join_count-1
            project.save()
            return JsonResponse({'status':True})
        else:
            return JsonResponse({'status':False,'msg':'你不想退出吧'})
    return render(request, 'platform/setting/project_setting_exit.html')
@csrf_exempt
def project_invite_view(request,project_id):

    if request.method == 'POST':
        data_dict={"status":False}
        form = InviteForm(data=request.POST)
        if form.is_valid():
            form.instance.project=request.tracer.project
            form.instance.creator=request.tracer.user
            code=random.randint(100000, 999999)
            form.instance.code=code
            instance=form.save()
            data_dict["status"]=True
            data_dict['code']="{scheme}://{host}{path}".format(
                scheme=request.scheme,
                host=request.get_host(),
                path=reverse('invite_join', kwargs={'code': code})
            )
            return JsonResponse(data_dict)
        else:
            data_dict["Error"]=form.errors
            return JsonResponse(data_dict)


    if request.method == 'GET':
        invites = ProjectInvite.objects.filter(project_id=project_id)
        if request.tracer.user != request.tracer.project.creator:
            Emsg = "没有权限查看，请联系项目创建者"
            return render(request, 'platform/setting/project_invite.html', {'Emsg': Emsg,'invites':invites})
        form = InviteForm()
        return render(request, 'platform/setting/project_invite.html',{'form':form,'invites':invites})

@csrf_exempt
def invite_join(request, code):
    """ 访问邀请码 """
    # 初步校验
    invite_object = ProjectInvite.objects.filter(code=code).first()
    if not invite_object:
        return render(request, 'platform/invite_join.html', {'error': '邀请码不存在'})

    if invite_object.project.creator == request.tracer.user:
        return render(request, 'platform/invite_join.html', {'error': '创建者无需再加入项目'})

    exists = ProjectUser.objects.filter(project=invite_object.project, user=request.tracer.user).exists()
    if exists:
        return render(request, 'platform/invite_join.html', {'error': '已加入项目无需再加入'})

    # 如果只是访问则返回显示
    if request.method == 'GET':
        limit_datetime = invite_object.create_datetime + datetime.timedelta(minutes=invite_object.period)
        limit_datetime = limit_datetime.replace(tzinfo=None)  # 去掉时区 好做比较
        avliable_datetime = limit_datetime-datetime.datetime.now()
        avliable_days = avliable_datetime.days
        avliable_hours, remainder = divmod(avliable_datetime.seconds, 3600)
        avliable_minutes, avliable_seconds = divmod(remainder, 60)
        avliable_datetime = "{:02d}天 {:02d}小时 {:02d}分钟 {:02d}秒".format(avliable_days, avliable_hours,
                                                                                   avliable_minutes, avliable_seconds)

        return render(request, 'platform/invite_join.html', {'project': invite_object.project,'avliable_datetime':avliable_datetime})

    # 开始更深入的校验，
    if request.method == 'POST':
        current_datetime = datetime.datetime.now()

        # ####### 价格策略最多允许的成员(要进入的项目的创建者的限制）#######
        # 是否已过期，如果已过期则使用免费额度
        max_transaction = Transaction.objects.filter(user=invite_object.project.creator).order_by('-id').first()
        if max_transaction.price_policy.category == 1:
            max_member = max_transaction.price_policy.project_member
        else:
            if max_transaction.end_datetime < current_datetime:
                free_object = PricePolicy.objects.filter(category=1).first()
                max_member = free_object.project_member
            else:
                max_member = max_transaction.price_policy.project_member

        # 只看项目参与者数量（不算项目创建者）
        current_member = ProjectUser.objects.filter(project=invite_object.project).count()
        current_member = current_member + 1
        if current_member >= max_member: #如果加入后的数量大于最大，则不让其加入
            return render(request, 'platform/invite_join.html', {'error': '项目成员超限，请项目创建者升级套餐'})

        # 邀请码是否过期
        limit_datetime = invite_object.create_datetime + datetime.timedelta(minutes=invite_object.period)
        limit_datetime = limit_datetime.replace(tzinfo=None) #去掉时间 好做比较
        if current_datetime > limit_datetime:
            invite_object.delete()
            return render(request, 'platform/invite_join.html', {'error': '邀请码已过期'})

        # 数量限制
        if invite_object.count:
            if invite_object.use_count >= invite_object.count:
                invite_object.delete()
                return render(request, 'platform/invite_join.html', {'error': '邀请码次数已使用完'})
            invite_object.use_count += 1
            invite_object.save()


        ProjectUser.objects.create(user=request.tracer.user, project=invite_object.project)

        # ####### 问题2： 更新项目参与成员 #######
        invite_object.project.join_count += 1
        invite_object.project.save()

        return render(request, 'platform/invite_join.html', {'project': invite_object.project,'success': '已加入项目'})