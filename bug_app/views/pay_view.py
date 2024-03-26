import json
from datetime import datetime, timedelta

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django_redis import get_redis_connection

from bug_app.models import PricePolicy, Transaction
from bug_app.utils import uuidStr
from bug_app.utils.alipay import AliPay

#展示所有商品
def show_pay_view(request):
    policys = PricePolicy.objects.all()
    return render(request, 'index/index_price.html', {'policys': policys})
# 用户确认支付页面，预生产订单
def payment_view(request):
    if request.method == 'GET':
        return render(request, 'account/payment.html', {'error': "发生错误,没有获取到信息"})

    # 创建购买订单预览页面
    # ,count,policy_id
    count = int(request.POST.get('quantity'))
    policy_id = request.POST.get('policy_id')
    Policy = PricePolicy.objects.get(id=policy_id)
    if not Policy or count < 1:
        return render(request, 'account/payment.html', {'error': "发生错误或者套餐不存在"})
    price = Policy.price
    Amount = price * count

    # 将待生成订单信息放到内存中30分钟
    data=[Policy.id,Amount,count]
    data_json = json.dumps(data)
    conn = get_redis_connection('default')
    conn.set('payment_' + request.tracer.user.mobile_phone, data_json, ex=60 * 30)

    return render(request, 'account/payment.html',{'price_policy':Policy,'Amount':Amount,'count':count})

#用户确认后，创建订单，跳转支付页面
def pay_view(request):
    # 发起支付页面
    # 先从内存中查看是否有30分钟内的待生成订单数据
    conn = get_redis_connection('default')
    data = conn.get('payment_' + request.tracer.user.mobile_phone)

    # 没有就属于新创建操作
    if data is not None:
        data_list = json.loads(data.decode('utf-8'))
        # 创建新的订单
        instance = Transaction.objects.create(
            order=uuidStr.generate_order_number(), status=1, price_policy_id=data_list[0], price=data_list[1],
            user=request.tracer.user,
            count=data_list[2],

        )

        # 初始化支付宝操作
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=settings.PAY_TEST_URL+"/user/pay/notify/",  # 公网IP 支付成功后 支付宝会向这个url post数据
            return_url=settings.PAY_TEST_URL+"/user/pay/notify/", #get请求 支付成功后跳转页面
            app_private_key_path=settings.APP_PRIVATE_KEY_PATH,
            alipay_public_key_path=settings.ALIPAY_PUBLIC_KEY_PATH,
        )
        # 初始化 订单数据，返回签名后的参数数据
        query_params = alipay.direct_pay(
            subject="Tracer的VIP套餐",     # 商品描述
            out_trade_no=instance.order,    #订单号
            total_amount=instance.price     #价格金额
        )
        # 构造支付URL
        pay_url = "{}?{}".format(settings.ALIPAY_GATEWAY_URL, query_params)
        #跳转支付
        return redirect(pay_url)
    else:
        return HttpResponse('没有待支付信息')

#支付完成后回调处理的url
def pay_notify_view(request):
    alipay = AliPay(
        appid=settings.ALIPAY_APPID,
        app_notify_url="http://localhost:8000/user/pay/notify/",  # 公网IP 支付成功后 支付宝会向这个url post数据
        return_url="http://localhost:8000/user/pay/notify/",  # get请求 支付成功后跳转页面
        app_private_key_path=settings.APP_PRIVATE_KEY_PATH,
        alipay_public_key_path=settings.ALIPAY_PUBLIC_KEY_PATH,
    )
    if request.method == 'GET':
        # 生产环境只做跳转
        # 或者根据校验结果判断是否支付成功

        if settings.DEBUG:# 测试环境
            parms = request.GET.dict()
            sign = parms.pop('sign', None)
            status = alipay.verify(parms, sign) #bool
            if status:
                order_id=parms.pop('out_trade_no', None)
                print(order_id)
                obj=Transaction.objects.filter(order=order_id).first()
                obj.status = 2
                obj.start_datetime=datetime.now()
                obj.end_datetime=datetime.now() + timedelta(days=365 * obj.count)
                obj.save()
        return redirect("/user/info/")
    elif request.method == 'POST':
        # 查看是否支付成功，做订单信息更新支付
        # 支付宝会将订单号返回,还会返回签名认证
        # 我们可以通过使用支付宝公钥校验返回的数据，判断这些数据是否有效
        parms = request.POST.dict()
        sign=parms.pop('sign',None)
        status = alipay.verify(parms, sign)
        if status:
            order_id=parms.pop('out_trade_no', None)
            print(order_id)
            obj=Transaction.objects.filter(order=order_id).first()
            obj.status = 2
            obj.start_datetime=datetime.now()
            obj.end_datetime=datetime.now() + timedelta(days=365 * obj.count)
            obj.save()
            return HttpResponse('success')
        return HttpResponse('error')

