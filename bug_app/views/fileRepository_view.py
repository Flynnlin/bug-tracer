from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from bug_app.models import FileRepository, Project, Transaction, PricePolicy
from bug_app.utils import oss, is_url


def fileRepository_list_view(request,project_id):
    folder_id = request.GET.get('folder_id',None)
    path=[]
    if not folder_id:
        #根目录
        file = FileRepository.objects.filter(project_id=project_id, parent__isnull=True).order_by('-file_type')
    else:
        #查询当前的文件夹
        file_obj = FileRepository.objects.filter(id=folder_id,file_type=2,project_id=project_id).first()
        # 初始化爸爸是自己
        parent_obj = file_obj
        while parent_obj:
            # 如果爸爸存在，则说明自己不是根，将自己添加到最后
            # print(file_obj.parent.name)
            path.insert(0,parent_obj)
            # 爸爸的爸爸，即向上递归
            parent_obj = parent_obj.parent

        file = FileRepository.objects.filter(project_id=project_id, parent_id=folder_id).order_by('-file_type')

    return render(request,'platform/fileRepository/fileRepository_list.html',{'path':path,'folder_id':folder_id,'files':file})


# TODO: 上传文件的过程可以优化为前端上传文件，
#  且上传到OSS的文件改名为随机字符串，新增一个字典来存储对应关系，这样文件改名就可以只改数据表即可
#   后端上传性能较慢，大文件不友好 用户体验不好
@csrf_exempt
def fileRepository_upload_view(request,project_id):
    folder_id = request.GET.get('folder', None)
    #获取文件相关内容
    file_type = request.POST.get('file_type')
    if file_type == '1':
        file_obj = request.FILES.get("file")
        file_name = file_obj.name
        file_size = file_obj.size
    elif file_type == '2':
        file_obj = ''
        file_name = request.POST.get('file')
        file_size = 0
    else:
        return JsonResponse({'status':False,'msg':"类型错误"})
    path = 'fileRepository/' + request.POST.get('path', '') + file_name

    data_dict = {}
    data_dict['status'] = True
    data_dict['file_name'] = file_name
    data_dict['file_size'] = file_size
    data_dict['path'] = path
    data_dict['folder_id'] = folder_id

    # 上传到OSS
    bucket_name=Project.objects.get(id=project_id).bucket
    cloud=oss.ConnectOss()
    if file_type == '1':
        # 先判断是否余额充足
        max_transaction = Transaction.objects.filter(user=request.tracer.project.creator).order_by('-id').first()
        if max_transaction.price_policy.category == 1:
            pricePolicy = max_transaction.price_policy
        else:
            if max_transaction.end_datetime < datetime.datetime.now():
                pricePolicy = PricePolicy.objects.filter(category=1).first()
            else:
                pricePolicy = max_transaction.price_policy


        project_space = pricePolicy.project_space #单个桶的空间大小
        per_file_size = pricePolicy.per_file_size #单个文件的大小
        storage = Project.objects.get(id=project_id).use_space # 已使用大小
        if per_file_size<=file_size:
            data_dict['msg'] = '文件过大，请升级套餐'
            data_dict['status'] = False
        elif storage+file_size>project_space:
            data_dict['msg'] = '存储空间不足，请升级套餐'
            data_dict['status'] = False
        if data_dict['status']==False: #上传失败直接返回
            return JsonResponse(data_dict)
        # 上传文件
        url=cloud.upload_file(bucket_name,path,file_obj)
        if not is_url.is_https_url(url):
            data_dict['status'] = False
            data_dict['msg'] = url
            return JsonResponse(data_dict)
    elif file_type == '2':
        #创建文件夹  目录需以正斜线结尾。
        cloud.create_folder(bucket_name,path+'/')
        url = ''
    else:
        return JsonResponse({'status':False,'msg':"类型错误"})

    #添加文件记录
    file_path=url
    parent_id=folder_id
    update_user=request.tracer.user

    file=FileRepository.objects.create(project=request.tracer.project,
                                  name=file_name,update_user=update_user)
    if parent_id != 'None':
        file.parent_id=parent_id
        file.save()
    if file_type == '2':
        file.file_type=2
        file.save()
    elif file_type == '1':
        file.file_size=file_size
        file.file_path=file_path
        file.save()

        #项目表已用空间大小添加
        Project.objects.filter(id=project_id).update(use_space=file_size+storage)

    return JsonResponse(data_dict)

@csrf_exempt
def fileRepository_delete_view(request,project_id):
    # 需要 bucket、path
    # 需要 FileRepository——obj id

    file_id = request.POST.get('file_id',False)
    path=request.POST.get('path',False)
    file=FileRepository.objects.get(id=file_id)
    if not path:
        path = ''
    path='fileRepository/'+path+file.name
    if file.file_type == 2:
        path+='/'

    # 删除file记录表， 数据库设置级联删除
    FileRepository.objects.filter(id=file_id).delete()

    # oss 删除
    bucket_name = Project.objects.get(id=project_id).bucket
    cloud = oss.ConnectOss()
    print(path)
    if file.file_type == 1:
        cloud.delete_file(bucket_name,path)
    if file.file_type == 2:
        cloud.delete_folder(bucket_name,path)

    return JsonResponse({'status': True, 'msg': "成功"})
