from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from bug_app.forms.issues_form import IssuesForm, IssuesReplyModelForm
from bug_app.models import Issues, IssuesReply
from bug_app.utils.pagination import Pagination

#问题列表
def issue_view(request,project_id):

    query={'project_id':project_id}

    issue_list = Issues.objects.filter(**query)
    page_obj = Pagination(issue_list, request)
    page_queryset = page_obj.page_queryset
    page_string = page_obj.generate_pagination_html()
    return render(request,'platform/issue/issue.html',{'issues':page_queryset,'page_string':page_string})

# 添加问题
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


# 更新问题
def issue_edit_view(request,project_id,issue_id):
    issue=Issues.objects.get(id=issue_id)
    if request.method=='POST':
        form = IssuesForm(request.POST,instance=issue, request=request)
        if form.is_valid():
            form.save()

        else:
            return render(request, 'platform/issue/issue_detail_update.html', {"form": form, "issue":issue})

    if request.method=="GET":
        form = IssuesForm(instance=issue,request=request)
        return render(request,'platform/issue/issue_detail_update.html',{"form": form, "issue":issue})


# 问题历史记录
# 新建问题评论
@csrf_exempt
def issue_get_reply_view(request,project_id,issue_id):
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
    if request.method=="POST":
        data_dict={'status': False}
        form = IssuesReplyModelForm(request.POST)
        if form.is_valid():
            form.instance.issues_id = issue_id
            form.instance.creator = request.tracer.user
            form.instance.reply_type = 2
            row=form.save()
            # 将添加到数据库的实例再返回给页面，页面上显示处理
            data = {
                'id': row.id,
                'reply_type_text': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.username,
                'datetime': row.create_datetime.strftime("%Y-%m-%d %H:%M"),
                'parent_id': row.reply_id
            }

            data_dict = {'status': True,'data': data}
        else:
            data_dict['error']=form.errors
        return JsonResponse(data_dict)
