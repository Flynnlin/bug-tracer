from django.utils.safestring import mark_safe


class CheckFilter(object):
    """
    CheckFilter类用于生成复选框过滤器的HTML代码。

    Attributes:
        name (str): 过滤器的名称。
        data_list (list): 包含键值对的列表，用于生成每个复选框的文本和值。
        request (HttpRequest): 当前请求对象，用于获取URL参数。

    Methods:
        __init__(self, name, data_list, request): 初始化CheckFilter对象。
        __iter__(self): 生成器方法，用于生成每个复选框的HTML代码。
    """

    def __init__(self, name, data_list, request):
        """
        初始化CheckFilter对象。

        Args:
            name (str): 过滤器的名称。
            data_list (list): 包含键值对的列表，用于生成每个复选框的文本和值。
            request (HttpRequest): 当前请求对象，用于获取URL参数。
        """
        self.name = name
        self.data_list = data_list  # 当前字段的条件组 是一个元组列表
        self.request = request

    def __iter__(self):
        """
        生成器方法，用于生成每个复选框的HTML代码。

        Yields:
            str: 包含HTML代码的字符串，表示一个复选框。
        """
        # self.data_list 类似 <QuerySet [(2, '任务'), (3, '功能'), (4, 'Bug')]>
        for item in self.data_list:
            key = str(item[0])  # 帅选条件的值
            text = item[1]
            ck = ""  # 选择框是否选中标记

            # 检查当前项是否被选中
            # 即查看request中传入的筛选条件是否有，如果对应则说明选中状态
            # 获取当前字段已被选中的值
            value_list = self.request.GET.getlist(self.name)  # [2、3、]
            if key in value_list:
                # 如果当前当前处理的值在已经已选中列表中
                # 则将其移除列表
                # 添加html选中效果
                ck = 'checked'
                value_list.remove(key)
            else:
                # 如果当前值是未选择 的值，则将其加入到列表中
                value_list.append(key)
            # value_list：此时两种情况
            ## 如果当前值是被选择状态，则value_list中就是除去当前值后的所有被选中值
            ## 如果当前值没有被选中，则value_list中就是所有已选中值再加上当前值

            # 生成URL参数
            # 获取所有字段当前筛选条件
            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            # 更新当前字段的筛选条件
            # 将当前筛选条件字段名和更新后的value_list放进去
            # 达到的效果是如果当前值已经被选中，则点击生成后的url就是取消当前值选中
            # 如果当前值没有被选中，则点击后就是在当前筛选条件上增加字节的筛选条件
            query_dict.setlist(self.name, value_list)
            # 移除可能存在的页码参数、即置为第一页
            if 'page' in query_dict:
                query_dict.pop('page')
            # 生成最终的URL
            param_url = query_dict.urlencode()  # 输出类似 is=2&is=4
            if param_url:
                url = "{}?{}".format(self.request.path_info, param_url)
            else:
                url = self.request.path_info

            # 组合拼接生成HTML代码
            html = ('<a class="cell" href="{url}"><input type="checkbox" {ck} /><label>{text}</label></a>'
                    .format(url=url, ck=ck, text=text))
            yield mark_safe(html)


class SelectFilter(object):
    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        yield mark_safe("<select class='singleSelect' multiple='multiple' style='width:100%;' >")
        for item in self.data_list:
            key = str(item[0])
            text = item[1]

            selected = ""
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                selected = 'selected'
                value_list.remove(key)
            else:
                value_list.append(key)

            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.name, value_list)

            if 'page' in query_dict:
                query_dict.pop('page')

            param_url = query_dict.urlencode()
            if param_url:
                url = "{}?{}".format(self.request.path_info, param_url)  # status=1&status=2&status=3&xx=1
            else:
                url = self.request.path_info

            html = "<option value='{url}' {selected} >{text}</option>".format(url=url, selected=selected, text=text)
            yield mark_safe(html)
        yield mark_safe("</select>")


class dateFilter(object):
    def __init__(self, request):
        self.request = request

    def __iter__(self):
        html=""
        if self.request.GET.get("start_date"):
            html += '<input type="text" name="start_date" placeholder="开始时间" class="form-control" id="id_start_date" value="{}">'.format(str(self.request.GET.get("start_date")))
        else:
            html = '<input type="text" name="start_date" placeholder="开始时间" class="form-control" id="id_start_date">'
        if self.request.GET.get("end_date",""):
            html += '<input type="text" name="end_date" placeholder="结束时间" class="form-control" id="id_end_date" value="{}">'.format(str(self.request.GET.get("end_date","")))
        else:
            html += '<input type="text" name="end_date" placeholder="结束时间" class="form-control" id="id_end_date">'
        yield mark_safe(html)
