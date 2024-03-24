import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from bug_app.forms.issues_form import IssuesForm, IssuesReplyModelForm
from bug_app.models import Issues, IssuesReply, ProjectUser, IssuesType
from bug_app.utils.pagination import Pagination
from bug_app.utils.filter_yield import CheckFilter,SelectFilter,dateFilter

# 问题列表
def issue_view(request, project_id):
    query = {'project_id': project_id}
    # 添加筛选条件
    allow_filter = ['issues_type', 'status', 'priority', 'start_date', 'end_date', 'attention', 'assign']
    for name in allow_filter:
        value_list = request.GET.getlist(name)  # 取参数值
        if not value_list:  # 如果没有值则不添加筛选条件
            continue
        if name == "start_date":
            query["{}__gte".format(name)] = value_list[0]
        elif name == "end_date":
            query["{}__lte".format(name)] = value_list[0]
        else:
            query["{}__in".format(name)] = value_list  # 添加筛选条件
    print(query)
    issue_list = Issues.objects.filter(**query)
    # 得到分页
    page_obj = Pagination(issue_list, request)
    page_queryset = page_obj.page_queryset
    page_string = page_obj.generate_pagination_html()

    # 筛选框html代码
    # 获取当前项目的项目类型键值对
    project_issues_type = IssuesType.objects.filter(project_id=project_id).values_list('id', 'title')
    # 获取当前项目的所有用户
    project_total_user = [(request.tracer.project.creator_id, request.tracer.project.creator.username,)]
    join_user = ProjectUser.objects.filter(project_id=project_id).values_list('user_id', 'user__username')
    project_total_user.extend(join_user)
    filter_list = [
        {'title': "时间区域", 'filter': dateFilter(request)},
        {'title': "问题类型", 'filter': CheckFilter('issues_type', project_issues_type, request)},
        {'title': "状态", 'filter': CheckFilter('status', Issues.status_choices, request)},
        {'title': "优先级", 'filter': CheckFilter('priority', Issues.priority_choices, request)},
        {'title': "指派者", 'filter': SelectFilter('assign', project_total_user, request)},
        {'title': "关注者", 'filter': SelectFilter('attention', project_total_user, request)},
    ]
    return render(request, 'platform/issue/issue.html',
                  {'issues': page_queryset, 'page_string': page_string,
                   'filter_list': filter_list})


# 添加问题
def issue_add_view(request, project_id):
    if request.method == 'POST':
        data_dict = {}
        form = IssuesForm(request.POST, request=request)
        if form.is_valid():
            form.instance.creator = request.tracer.user
            form.instance.project = request.tracer.project
            form.save()
            data_dict['status'] = True
        else:
            data_dict['status'] = False
            data_dict['Error'] = form.errors
        return JsonResponse(data_dict)

    form = IssuesForm(request=request)
    return render(request, 'platform/issue/issue_add.html', {'form': form})


# 更新问题
# 显示历史记录-评论
@csrf_exempt
def issue_edit_view(request, project_id, issue_id):
    issue = Issues.objects.filter(id=issue_id, project_id=project_id).first()
    if request.method == 'POST':
        data_dict = {'status': False}
        response_dict = json.loads(request.body.decode('utf-8'))

        # Issue 更新
        instance = issue
        field = Issues._meta.get_field(response_dict['name'])
        ##判断是否允许为空
        if not response_dict['value']:  # 如果value是空值
            if not field.null:
                data_dict['error'] = "该值不允许为空"
                return JsonResponse(data_dict)
            response_dict['value'] = None

        ## 权限校验：普通外键字段
        if response_dict['name'] in ['issues_type', 'module', 'parent', 'assign']:
            if response_dict['name'] == 'assign':
                # 是否是项目创建者
                if response_dict['value'] == str(request.tracer.project.creator_id):
                    response_dict['value'] = request.tracer.project.creator
                else:  # 则是参与者
                    project_user_object = ProjectUser.objects.filter(project_id=project_id,
                                                                     user_id=response_dict['value']).first()
                    if project_user_object:
                        response_dict['value'] = project_user_object.user
                    else:  # 判断为无权限
                        response_dict['value'] = None

            else:
                # 条件判断：用户输入的值，是自己的值。
                response_dict['value'] = field.related_model.objects.filter(id=response_dict['value'],
                                                                            project_id=project_id).first()

        ## 多对多外键字段 校验
        if response_dict['name'] in ["attention"]:
            # {"name":"attention","value":[1,2,3]}
            # 和其他字段不一样的是，它的值是一个列表
            if response_dict['value'] == None:
                response_dict['value'] = []
            if not isinstance(response_dict['value'], list):
                return JsonResponse({'status': False, 'error': "数据格式错误"})
            print(response_dict)
            # values=["1","2,3,4]  ->   id是否是项目成员（参与者、创建者）
            # 获取当前项目的所有成员
            user_dict = {str(request.tracer.project.creator_id): request.tracer.project.creator.username}
            project_user_list = ProjectUser.objects.filter(project_id=project_id)
            for item in project_user_list:
                user_dict[str(item.user_id)] = item.user.username
            # 检查输入的id是否存在合法数据中
            username_list = []
            for user_id in response_dict['value']:
                username = user_dict.get(str(user_id))
                if not username:
                    return JsonResponse({'status': False, 'error': "用户不存在请重新设置"})
                username_list.append(username)
            # response_dict['value']=username_list

        ## choice 字段
        if response_dict['name'] in ['priority', 'status', 'mode']:
            selected_text = None
            for key, text in field.choices:
                if str(key) == response_dict['value']:
                    selected_text = text
            if not selected_text:
                return JsonResponse({'status': False, 'error': "您选择的值不存在"})

        # 所有条件通过

        if response_dict['name'] in ["attention"]:
            # many-to-many set 需要单独处理
            instance.attention.set(response_dict['value'])
            instance.save()
            ustr = ""
            for u in username_list:
                ustr += (u + "、")
            msg = "{}更新了为{}".format(field.verbose_name, ustr[:-1])
        else:
            setattr(instance, response_dict['name'], response_dict['value'])
            instance.save()
            msg = "{}更新了为{}".format(field.verbose_name, str(response_dict['value']))

        # 生成操作记录
        op = IssuesReply.objects.create(
            reply_type=1,
            issues=issue,
            creator=request.tracer.user,
            content=msg,
        )
        data = {
            'id': op.id,
            'reply_type_text': op.get_reply_type_display(),
            'content': op.content,
            'creator': op.creator.username,
            'datetime': op.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': op.reply_id
        }
        data_dict['status'] = True
        data_dict['data'] = data
        return JsonResponse(data_dict)

    if request.method == "GET":
        form = IssuesForm(instance=issue, request=request)
        return render(request, 'platform/issue/issue_detail_update.html', {"form": form, "issue": issue})


# 问题历史记录
# 新建问题评论
@csrf_exempt
def issue_get_reply_view(request, project_id, issue_id):
    # 获取所有历史记录
    if request.method == "GET":
        reply_list = IssuesReply.objects.filter(issues_id=issue_id)
        # 将queryset转换为json格式
        data_list = []
        for row in reply_list:
            data = {
                'id': row.id,
                'reply_type_text': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.username,
                'datetime': row.create_datetime.strftime("%Y-%m-%d %H:%M"),
                'parent_id': row.reply_id
            }
            data_list.append(data)

        return JsonResponse({'status': True, 'data': data_list})

    # 新建记录
    if request.method == "POST":
        data_dict = {'status': False}
        form = IssuesReplyModelForm(request.POST)
        if form.is_valid():
            form.instance.issues_id = issue_id
            form.instance.creator = request.tracer.user
            form.instance.reply_type = 2
            row = form.save()
            # 将添加到数据库的实例再返回给页面，页面上显示处理
            data = {
                'id': row.id,
                'reply_type_text': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.username,
                'datetime': row.create_datetime.strftime("%Y-%m-%d %H:%M"),
                'parent_id': row.reply_id
            }

            data_dict = {'status': True, 'data': data}
        else:
            data_dict['error'] = form.errors
        return JsonResponse(data_dict)
