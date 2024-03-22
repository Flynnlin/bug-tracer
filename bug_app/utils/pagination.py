class Pagination(object):
    def __init__(self, queryset, request, page_param="page", page_size=7, page_number=1):
        # 参数：数据查询结果集、用户请求参数、page的参数名（默认为page）
        #      、一页展示记录的数量(默认5）、显示当前页的前i页和后i页的跳转按钮(默认1)

        self.page_param = page_param
        # page的参数名

        page = request.GET.get(page_param, "1")
        if page.isnumeric():
            self.page = int(page)
        else:
            self.page = 1
        # 获取了需要请求的page页数

        self.start_index = (self.page - 1) * page_size  # 当前页记录起始位
        self.end_index = (self.page) * page_size  # 当前页记录结束位

        self.page_queryset = queryset[self.start_index:self.end_index]
        # 需要显示的分页数据

        self.total_count = queryset.count()
        self.page_count = self.total_count // page_size + 1
        # 记录的总数量、总页数

        self.page_number = page_number
        # 页面跳转按钮数量

        # 保留搜索条件（原来的其他搜索条件）
        self.params = request.GET.copy()
        self.params['page'] = self.page

    def generate_pagination_html(self):
        # 显示当前页的前3页和后3页的跳转按钮
        # 显示上一页和下一页按钮
        html_str = '<nav aria-label="Page navigation"><ul class="pagination justify-content-center">'

        if self.page > 1:
            self.params["page"] = self.page - 1
            html_str += f'<li class="page-item"><a class="page-link" href="?{self.params.urlencode()}">上一页</a></li>'

        for i in range(max(1, self.page - self.page_number), min(self.page + self.page_number, self.page_count) + 1):
            if i == self.page:
                html_str += f'<li class="page-item active"><a class="page-link" href="?{self.params.urlencode()}">{i}</a></li>'
            else:
                self.params["page"] = i
                html_str += f'<li class="page-item"><a class="page-link" href="?{self.params.urlencode()}">{i}</a></li>'

        if self.page < self.page_count:
            self.params["page"] = self.page + 1
            html_str += f'<li class="page-item"><a class="page-link" href="?{self.params.urlencode()}">下一页</a></li>'

            # 添加跳转输入框（小小bug 可笑可笑《两个【page
        html_str += '''
                    <li class="page-item">
                        <input type="number" class="form-control" id="jumpPage" min="1" max="{page_count}" placeholder="{page_count}">
                    </li>
                    <li class="page-item">
                        <button class="btn btn-primary" onclick="jumpToPage()">跳转</button>
                    </li>
                    <script>
                        function jumpToPage() {{
                            var pageInput = document.getElementById("jumpPage").value;
                            if (pageInput >= 1 && pageInput <= {page_count}) {{
                                var url = "?{params}&page=" + pageInput;
                                window.location.href = url;
                            }}
                        }}
                    </script>
                '''.format(page_count=self.page_count, params=self.params.urlencode())

        html_str += '</ul></nav>'
        return html_str