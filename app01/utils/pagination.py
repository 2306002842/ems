from copy import deepcopy

from django.utils.html import escape
from django.utils.safestring import mark_safe


class Pagination(object):
    """ 分页工具类：根据查询集生成当前页数据和底部分页 HTML """

    def __init__(self, request, queryset, page_size=10, page_param="page", plus=5):
        """
        :param request: 请求对象，用来读取页码、保留其他查询参数（如搜索词 q）
        :param queryset: 已经筛选、排序好的数据集合
        :param page_size: 每页显示多少条
        :param page_param: 页码参数名，例如 /pretty/list/?page=2 中的 page
        :param plus: 页码区域显示当前页前后各几页
        """
        # 复制 request.GET：QueryDict 默认不可修改，deepcopy 后放开 _mutable 才能改页码
        query_dict = deepcopy(request.GET)
        query_dict._mutable = True
        self.query_dict = query_dict
        self.page_param = page_param

        # 读取页码；不是纯数字时一律当作第 1 页
        page = request.GET.get(page_param, "1")
        page = int(page) if page.isdecimal() else 1

        # 计算总页数：总条数 / 每页条数，有余数就再补一页
        total_count = queryset.count()
        total_page_count, div = divmod(total_count, page_size)
        if div:
            total_page_count += 1
        # 数据为空时也保留 1 页，避免出现“第 0 页”
        if total_page_count == 0:
            total_page_count = 1
        self.total_page_count = total_page_count

        # 页码越界时自动修正：小于 1 取 1，大于总页数取最后一页
        if page < 1:
            page = 1
        if page > total_page_count:
            page = total_page_count
        self.page = page
        self.page_size = page_size
        self.plus = plus

        # 按页码切片，取出当前页要显示的数据
        start = (page - 1) * page_size
        end = page * page_size
        self.page_queryset = queryset[start:end]

    def html(self):
        """ 生成分页条 HTML：首页 / 上一页 / 页码 / 下一页 / 尾页 / 页码跳转 """
        # 计算页码显示范围：数据少时全部显示；数据多时显示当前页前后各 plus 页
        if self.total_page_count <= 2 * self.plus + 1:
            start_page = 1
            end_page = self.total_page_count
        elif self.page <= self.plus:
            start_page = 1
            end_page = 2 * self.plus + 1
        elif self.page + self.plus > self.total_page_count:
            start_page = self.total_page_count - 2 * self.plus
            end_page = self.total_page_count
        else:
            start_page = self.page - self.plus
            end_page = self.page + self.plus

        page_str_list = []

        # 首页
        self.query_dict.setlist(self.page_param, [1])
        page_str_list.append('<li><a href="?{}">首页</a></li>'.format(self.query_dict.urlencode()))

        # 上一页：已经在第 1 页时仍指向第 1 页
        prev_page = self.page - 1 if self.page > 1 else 1
        self.query_dict.setlist(self.page_param, [prev_page])
        page_str_list.append('<li><a href="?{}">上一页</a></li>'.format(self.query_dict.urlencode()))

        # 页码：当前页加 active 类显示高亮
        for i in range(start_page, end_page + 1):
            self.query_dict.setlist(self.page_param, [i])
            if i == self.page:
                ele = '<li class="active"><a href="?{}">{}</a></li>'.format(self.query_dict.urlencode(), i)
            else:
                ele = '<li><a href="?{}">{}</a></li>'.format(self.query_dict.urlencode(), i)
            page_str_list.append(ele)

        # 下一页：已经在最后一页时仍指向最后一页
        next_page = self.page + 1 if self.page < self.total_page_count else self.total_page_count
        self.query_dict.setlist(self.page_param, [next_page])
        page_str_list.append('<li><a href="?{}">下一页</a></li>'.format(self.query_dict.urlencode()))

        # 尾页
        self.query_dict.setlist(self.page_param, [self.total_page_count])
        page_str_list.append('<li><a href="?{}">尾页</a></li>'.format(self.query_dict.urlencode()))

        # 页码跳转表单：page 以外的参数（如搜索词 q）作为隐藏域带上，跳转时不丢搜索条件
        hidden_inputs = "".join(
            '<input type="hidden" name="{}" value="{}">'.format(escape(k), escape(v))
            for k, values in self.query_dict.lists()
            if k != self.page_param
            for v in values
        )
        search_string = (
            '<li><form style="float: left; margin-left: -1px;" method="get">'
            + hidden_inputs
            + '<input name="page" style="position: relative; float: left; display: inline-block; '
              'width: 80px; border-radius: 0;" type="text" class="form-control" placeholder="页码">'
            + '<button style="border-radius: 0;" class="btn btn-default" type="submit">跳转</button>'
            + '</form></li>'
        )
        page_str_list.append(search_string)

        # mark_safe：告诉模板这段 HTML 是安全的，直接渲染而不是转义
        return mark_safe("".join(page_str_list))
