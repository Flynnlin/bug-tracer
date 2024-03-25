import collections

from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render

from bug_app.models import Issues, IssuesType


def statistic_view(request, project_id):
    return render(request, 'platform/statistics/statistic.html')


def projectIssue_type_view(request, project_id):
    start_time = request.GET.get('start')
    end_time = request.GET.get('end')
    # 构造字典
    data_dict = collections.OrderedDict()
    types = IssuesType.objects.filter(project_id=project_id).values_list('title', flat=True)
    for i in range(0, len(types)):
        data_dict[types[i]] = {'name': types[i], 'y': 0}

    # 获取数据
    issue = (Issues.objects.filter(project_id=project_id, create_datetime__gte=start_time, create_datetime__lte=end_time)
             .values('issues_type__title').annotate(ct=Count('id')))
    # 构造数据
    for item in issue:
        data_dict[item['issues_type__title']]['y'] = item['ct']
    return JsonResponse({'status': True, 'data': list(data_dict.values())})

def projectUser_work_view(request, project_id):
    start_time = request.GET.get('start')
    end_time = request.GET.get('end')
    # 构造字典
    data_dict = collections.OrderedDict()
    categories=[]
    series={}
    # 指派到xx的问题数量， 按问题类型分组
    """
    categories=['A', 'B', 'C']   # A、B、C 三个人
    
    series=[{
        name: '新建',     #状态名
        data: [5, 3, 4]     # A用户有5个“新建”状态的问题，B有3个。。。。
    }]
    
    """
    issue_list=Issues.objects.filter(project_id=project_id,create_datetime__gte=start_time, create_datetime__lte=end_time).order_by('assign')
    # 初始化列表信息
    for issue in issue_list:
        if issue.assign: #初始化项目人员，唯一性
            if issue.assign.username not in categories:
                categories.append(issue.assign.username)
        # 初始化项目现有的各种状态列表
        if issue.status not in series.keys():
            series[issue.status]={
                'name': issue.get_status_display(),
                'data':[],
                'id':issue.status
            }
    # 遍历每个人，再去查每个人不同状态有几个数据
    for user in categories:
        for status in series.values():
            count=Issues.objects.filter(project_id=project_id, status=status['id'],assign__username=user,create_datetime__gte=start_time, create_datetime__lte=end_time).count()
            status['data'].append(count)
    # 剩下没有指派人的问题
    categories.append("未指派")
    for status in series.values():
        count = Issues.objects.filter(project_id=project_id,status=status['id'], assign=None,create_datetime__gte=start_time, create_datetime__lte=end_time).count()
        status['data'].append(count)

    data={
        'categories': categories,
        'series': list(series.values())
    }

    return JsonResponse({'status': True, 'data': data})