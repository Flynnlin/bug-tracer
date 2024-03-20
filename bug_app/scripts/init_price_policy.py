#导入django环境
from bug_app.scripts import base

from bug_app.models import PricePolicy

def add_price_policies():
    # 添加免费版价格策略
    if not PricePolicy.objects.filter(title="个人免费版").exists():
        free_policy = PricePolicy.objects.create(
            category=1,
            title="个人免费版",
            price=0,
            project_num=5,
            project_member=2,
            project_space=10*1024*1024,   #10MB--字节
            per_file_size=2*1024*1024,
        )

    # 添加VIP价格策略
    if not PricePolicy.objects.filter(title="VIP").exists():
        vip_policy = PricePolicy.objects.create(
            category=2,
            title="VIP",
            price=199,
            project_num=20,
            project_member=100,
            project_space=50 * 1024*1024*1024,  # 50G转换为字节
            per_file_size=500*1024*1024,
        )

    # 添加SVIP价格策略
    if not PricePolicy.objects.filter(title="SVIP").exists():
        svip_policy = PricePolicy.objects.create(
            category=2,
            title="SVIP",
            price=299,
            project_num=50,
            project_member=200,
            project_space=100 * 1024*1024*1024,  # 100G转换为字节
            per_file_size=1 * 1024*1024*1024,  # 1G转换为字节
        )

    print("价格策略添加成功！")



if __name__ == "__main__":
    # 调用添加价格策略的函数
    add_price_policies()
