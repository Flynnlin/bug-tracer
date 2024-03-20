import sys
import oss2
from django.conf import settings
class ConnectOss(object):
    def __init__(self):
        """验证权限"""
        # 从环境变量中获取访问凭证。运行本代码之前，请确保已设置环境变量OSS_ACCESS_KEY_ID和OSS_ACCESS_KEY_SECRET。
        self.endpoint = settings.OSS_ENDPOINT# 填写Bucket所在地域对应的Endpoint
        self.auth = oss2.Auth(settings.OSS_ACCESS_KEY_ID,settings.OSS_ACCESS_KEY_SECRET)
    #创建存储桶
    def create_bucket(self, bucket_name):
        bucket = oss2.Bucket(self.auth, self.endpoint, bucket_name)
        # 设置存储空间为私有读写权限。
        try:
            #创建了公有读写策略的bucket
            bucket.create_bucket(oss2.models.BUCKET_ACL_PUBLIC_READ_WRITE)
        except Exception as e:
            return e
        return bucket_name
    def delete_bucket(self, bucket_name):
        #只能删除空的bucket
        bucket = oss2.Bucket(self.auth, self.endpoint, bucket_name)
        try:
            bucket.delete_bucket()
        except Exception as e:
            print(e)
            return e
        return bucket_name
    def storage_bucket(self, bucket_name):
        """
        storage_size_in_bytes    : 存储空间的总存储量，单位为字节。
        object_count             : 存储空间中总的对象数量。
        multi_part_upload_count  : 存储空间中已初始化但未完成或未中止的多部分上传的数量。
        live_channel_count       : 存储空间中活动直播通道的数量。
        last_modified_time       : 此次获取存储信息的时间点，格式为时间戳，单位为秒。
        standard_storage         : 标准存储类型对象的存储量，单位为字节。
        standard_object_count    : 标准存储类型对象的数量。
        infrequent_access_storage: 低频访问存储类型对象的计费存储量，单位为字节。
        infrequent_access_real_storage: 低频访问存储类型对象的实际存储量，单位为字节。
        infrequent_access_object_count: 低频访问存储类型对象的数量。
        archive_storage          : 归档存储类型对象的计费存储量，单位为字节。
        archive_real_storage    : 归档存储类型对象的实际存储量，单位为字节。
        archive_object_count    : 归档存储类型对象的数量。
        cold_archive_storage   : 冷归档存储类型对象的计费存储量，单位为字节。
        cold_archive_real_storage : 冷归档存储类型对象的实际存储量，单位为字节。
        cold_archive_object_count : 冷归档存储类型对象的数量。
        """
        try:
            bucket = oss2.Bucket(self.auth, self.endpoint, bucket_name)
            # 获取存储空间的统计信息。
            result = bucket.get_bucket_stat()
            return result
        except Exception as e:
            return e








    ###################################################


    #####################################################
    def percentage(consumed_bytes, total_bytes):
        if total_bytes:
            rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
            print('\r{0}% '.format(rate), end='')
            sys.stdout.flush()
    def upload_file(self,bucket_name, remote_file_path,local_file_path):
        # 上传文件到OSS。
        # yourObjectName由包含文件后缀，不包含Bucket名称组成的Object完整路径，例如abc/efg/123.jpg。
        # yourLocalFile由本地文件路径加文件名包括后缀组成，例如/users/local/myfile.txt
        # local_file_path  接受文件对象
        # local_file_path 为''则表示创建文件夹，remote_file_path应该为文件夹名
        try:
            bucket = oss2.Bucket(self.auth, self.endpoint, bucket_name)
            if local_file_path == '': #创建文件夹
                # 目录名称，目录需以正斜线结尾。
                bucket.put_object(remote_file_path, local_file_path)
            elif isinstance(local_file_path, str):
                bucket.put_object_from_file(remote_file_path, local_file_path)
            else:
                bucket.put_object(remote_file_path, local_file_path.read())
        except Exception as e:
            return e
        # return bucket_name+'/'+remote_file_path
        return self.get_url_file(bucket_name, remote_file_path)
    def download_file(self,bucket_name,remote_file_path,local_file_path):
        # 下载OSS文件到本地文件。
        # yourObjectName由包含文件后缀，不包含Bucket名称组成的Object完整路径，例如abc/efg/123.jpg。
        # yourLocalFile由本地文件路径加文件名包括后缀组成，例如/users/local/myfile.txt。
        try:
            bucket = oss2.Bucket(self.auth, self.endpoint, bucket_name)
            bucket.get_object_to_file(remote_file_path, local_file_path)
        except Exception as e:
            return e
        return local_file_path

    def get_url_file(self,bucket_name,remote_file_path):
        url="https://{}.oss-cn-{}.aliyuncs.com/{}".format(bucket_name,"chengdu",remote_file_path)
        return url

    def rename_file(self,bucket_name,src_object_name,dest_object_name):
        #重命名文件本质上就是先复制一份，然后再把旧的删了
        try:
            bucket = oss2.Bucket(self.auth, self.endpoint, bucket_name)
            result = bucket.copy_object(bucket_name, src_object_name, dest_object_name)

            # 查看返回结果的状态。如果返回值为200，表示执行成功。
            print('result.status:', result.status)

            # 删除srcobject.txt。
            result_del = bucket.delete_object(src_object_name)

            # 查看返回结果的状态。如果返回值为204，表示执行成功。
            print('result.status:', result_del.status)
        except Exception as e:
            return e
        return self.get_url_file(bucket_name,dest_object_name)




    def file_list(self,bucket_name):
        pass
    def bucket_list(self):
        pass

    def delete_file(self,bucket_name,remote_file_path):
        try:
            bucket = oss2.Bucket(self.auth, self.endpoint, bucket_name)
            # yourObjectName表示删除OSS文件时需要指定包含文件后缀，不包含Bucket名称在内的完整路径，例如abc/efg/123.jpg。
            bucket.delete_object(remote_file_path)
        except Exception as e:
            return e
        return True


    def create_folder(self,bucket_name,remote_file_path):
        # 目录名称，目录需以正斜线结尾。
        try:
            bucket = oss2.Bucket(self.auth, self.endpoint, bucket_name)
            bucket.put_object(remote_file_path, '')
        except Exception as e:
            return e
        return True
    def delete_folder(self,bucket_name,remote_file_path):
        # 删除目录及目录下的所有文件。
        #remote_file_path="exampledir/"
        try:
            bucket = oss2.Bucket(self.auth, self.endpoint, bucket_name)
            for obj in oss2.ObjectIterator(bucket, prefix=remote_file_path):
                bucket.delete_object(obj.key)
        except Exception as e:
            return e
        return True


if __name__ == '__main__':
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bug_tracer.settings")
    import django
    django.setup()

    co = ConnectOss()
    result = co.delete_bucket('18382135936-226dcca716fa481395a97642e596adac')

    # print(str(co.storage_bucket('123kjsvdsasd').storage_size_in_bytes/1024)+'KB')

    # print(co.create_bucket('123kjsvdsasd'))
    # res=remote_file_path=co.upload_file('18382135936-15712c7f4dbf4657bc043243a0961508', 't1/b23.jpg', r'C:\Users\flynn\Downloads\biye-cuit\project\bug_tracer\uploads\editor\kali-menu.png')
    # result=co.get_url_file('18382135936-15712c7f4dbf4657bc043243a0961508',remote_file_path)
    # print(res)
