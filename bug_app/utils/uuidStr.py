import uuid

def generate_order_number():
    """
    生成随机号
    """
    order_number = uuid.uuid4().hex
    return order_number