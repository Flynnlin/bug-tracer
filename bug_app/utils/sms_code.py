import json

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from django.conf import settings
import random

def send_sms(code,number):
    """"
    阿里云发送短信

    """


    # 配置接口密钥和模板编号
    accessKeyId=settings.ACCESSKEY_ID
    accessKeySecret = settings.ACCESSKEY_SECRET
    TemplateCode =settings.TEMPLATEMODE['sms_code']

    template = {
        'code': code
    }
    client = AcsClient(accessKeyId, accessKeySecret, 'default')
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')  # https | http
    request.set_version('2017-05-25')
    # 以上部分是公用的不变
    request.set_action_name('SendSms')
    # set_action_name 这个是选择你调用的接口的名称，如：SendSms，SendBatchSms等
    request.add_query_param('RegionId', "default")
    # 这个参数也是固定的

    request.add_query_param('PhoneNumbers', number)  # 发给谁
    request.add_query_param('SignName', "神的口袋")  # 签名
    request.add_query_param('TemplateCode', TemplateCode)  # 模板编号
    request.add_query_param('TemplateParam', f"{template}")  # 发送验证码内容
    #生产环境
    response = client.do_action_with_exception(request)
    res=str(response, encoding='utf-8')

    #测试环境
    # res ='OK'
    print(res + code)

    if 'OK' in res:
        return True
    else:
        return json.loads(res)['Message']


def generate_sms_code():
    return ''.join(random.choices('0123456789', k=4))

if __name__ == '__main__':
    # 设置 Django 环境 测试
    import django
    django.setup()
    print(settings.ACCESSKEY_ID)
    # code=generate_sms_code()
    # send_sms(code,'1838215936')