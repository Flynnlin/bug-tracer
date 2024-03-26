import collections
import datetime
import time

from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from bug_app.forms.project_form import ProjectModelform
from bug_app.models import Project, ProjectUser, IssuesType, Issues, IssuesReply, Transaction, PricePolicy
from bug_app.utils import oss, uuidStr

"""
管理面板的进入

所有项目列表
项目收藏
项目面板

"""
#首页展示所有项目
def project_list_view(request):
    # 从中间件获取当前用户
    current_user=request.tracer.user

    # 创建
    if request.method == 'POST': #如果时post 则是获取新建项目数据
        rep_msg={}
        form=ProjectModelform(request.POST,request=request)
        if form.is_valid():
            #创建桶
            bucketName = "{}-{}".format(current_user.mobile_phone, uuidStr.generate_order_number())
            cloud=oss.ConnectOss()
            cloud.create_bucket(bucketName)

            form.instance.bucket=bucketName
            form.instance.region="chengdu"
            form.instance.creator=current_user
            instance =form.save()

            # 初始化项目默认问题类型、
            for i in IssuesType.PROJECT_INIT_LIST:
                IssuesType.objects.create(project=instance,title=i)


            rep_msg['status'] = True
        else:
            rep_msg['status'] = False
            rep_msg['errors']=form.errors
        return JsonResponse(rep_msg)

    # 显示页面-展示项目
    if request.method == 'GET':
        form = ProjectModelform() #项目创建的form

        # 创建的项目
        user_created_projects = request.tracer.created_projects
        # 参与的项目
        user_joined_projects = request.tracer.joined_projects
        # 设置是三个列表 收藏、创建、参加
        project_dict={'star':[],'created':[],'joined':[]}
        for project in user_created_projects:
            project_dict['star' if project.star else 'created'].append(project)
        for project in user_joined_projects:
            project_dict['star' if project.star else 'joined'].append(project.project)
        return render(request,'platform/project_list.html',{'form':form,'project_dict':project_dict})


# 项目收藏&取消
def project_star_view(request, project_type, project_id):
# 定义视图函数project_star_view，接受request、project_type和project_id参数
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

# 进入项目
@csrf_exempt
def project_dashboard_view(request, project_id):
    #当访问项目管理的url时，会触发中间件
    #鉴权 、记录project信息到request中
    if request.method == 'POST':
        """ 在概览页面生成highcharts所需的数据 """
        today = datetime.datetime.now().date()
        # 初始化两个时间轴
        date_dict = collections.OrderedDict()
        date_dict2 = collections.OrderedDict()
        for i in range(0, 30):
            date = today - datetime.timedelta(days=i)
            date_dict[date.strftime("%Y-%m-%d")] = [time.mktime(date.timetuple()) * 1000, 0]
        for i in range(0, 30):
            date = today - datetime.timedelta(days=i)
            date_dict2[date.strftime("%Y-%m-%d")] = [time.mktime(date.timetuple()) * 1000, 0]

        # 获取30天内的数据
        Issuesresult = (Issues.objects.filter(project_id=project_id,
                                      create_datetime__gte=today - datetime.timedelta(days=30))
                    # 新增查询列 ctime，为截取创建时间的日期| # mysql 时间格式函数 "DATE_FORMAT(bug_app_issues.create_datetime,'%%Y-%%m-%%d')"
                  .extra(select={'ctime': "strftime('%%Y-%%m-%%d',bug_app_issues.create_datetime)"})
                  # 根据ctime将记录分组，计算数量，此时记录只剩下两个字段，时间、次数
                  .values('ctime').annotate(ct=Count('id')))
        Replyresult = (IssuesReply.objects.filter(issues__project_id=project_id,
                                        create_datetime__gte=today - datetime.timedelta(days=30))
                  .extra(select={'ctime': "strftime('%%Y-%%m-%%d',bug_app_issuesreply.create_datetime)"})
                  .values('ctime')
                  .annotate(ct=Count('id')))

        for item in Issuesresult:
            date_dict[item['ctime']][1] = item['ct']
        d1 = list(date_dict.values())

        for item in Replyresult:
            date_dict2[item['ctime']][1] = item['ct']
        d2 = list(date_dict2.values())

        data = [d1,d2]
        return JsonResponse({'status': True, 'data':data })

    # 获取最大使用空间和已经使用容量 （0.0/10.0M）
    max_transaction = Transaction.objects.filter(user=request.tracer.project.creator,status=2).order_by('-id').first()
    if max_transaction.price_policy.category == 1:
        pricePolicy = max_transaction.price_policy
    else:
        if max_transaction.end_datetime < datetime.datetime.now():
            pricePolicy = PricePolicy.objects.filter(category=1).first()
        else:
            pricePolicy = max_transaction.price_policy
    max_storage = round(pricePolicy.project_space / (1024 * 1024), 2)
    storage = str(round(request.tracer.project.use_space/(1024 * 1024),2))+'/'+str(max_storage)+"M"
    # 获取最新的几条问题更新记录
    last_reply=IssuesReply.objects.filter(issues__project_id=project_id).order_by('-create_datetime')[:5]
    # 获取参与人员
    user_list=ProjectUser.objects.filter(project_id=project_id).order_by('-create_datetime')

    # 问题数据处理 各种状态有多少多少个
    status_dict = collections.OrderedDict()
    for key, text in Issues.status_choices:
        status_dict[key] = {'text': text, 'count': 0}
    issues_data = Issues.objects.filter(project_id=project_id).values('status').annotate(ct=Count('id'))
    for item in issues_data:
        status_dict[item['status']]['count'] = item['ct']
    print(status_dict)
    return  render(request,'platform/project_dashboard.html',{'storage':storage,'last_reply':last_reply,'user_list':user_list,'status_dict':status_dict})

