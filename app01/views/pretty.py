# 靓号管理视图
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.shortcuts import render, redirect

from app01 import models
from app01.utils.form import BootstrapModelForm
from app01.utils.pagination import Pagination


class PrettyModelForm(BootstrapModelForm):
    """
    靓号的 ModelForm 表单类。
    作用：根据 PrettyNum 模型自动生成表单字段（号码、价格、级别、状态），
    样式由 BootstrapModelForm 基类统一添加，无需在这里重复处理。
    """

    class Meta:
        # 绑定到靓号模型
        model = models.PrettyNum
        # 指定表单里要显示、可编辑的字段（写在这里的字段会被自动生成输入控件）
        fields = ["mobile", "price", "level", "status"]


class PrettyEditModelForm(BootstrapModelForm):
    """
    编辑靓号专用的表单：
    1. 用正则校验号码必须是 11 位手机号
    2. 校验号码是否和其他记录重复（排除自己）
    """

    # RegexValidator(r'^1[3-9]\d{9}$', '手机号格式错误')：
    # 以 1 开头、第二位 3-9、后面 9 位数字，共 11 位
    mobile = forms.CharField(
        label="号码",
        validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号格式错误')],
    )

    class Meta:
        model = models.PrettyNum
        fields = ["mobile", "price", "level", "status"]

    def clean_mobile(self):
        """ 字段级校验：Django 会自动调用 clean_字段名 方法 """
        txt_mobile = self.cleaned_data["mobile"]
        # 排除当前正在编辑的这一条，再检查号码是否已被其他记录占用
        exists = (
            models.PrettyNum.objects.exclude(id=self.instance.pk)
            .filter(mobile=txt_mobile)
            .exists()
        )
        if exists:
            raise ValidationError("手机号已存在")
        # 校验通过时，必须把值返回，否则该字段会变成 None
        return txt_mobile


def pretty_list(request):
    """ 靓号列表（支持按号码模糊搜索） """
    # 1. 从 URL 查询参数里取搜索关键词，例如 /pretty/list/?q=156
    #    get("q", "") 表示取不到 q 时返回空字符串，避免取值为 None 报错
    search_data = request.GET.get("q", "")

    # 2. 先用字典拼装查询条件，再用 ** 把字典展开后传给 filter
    #    （有搜索词就加条件，没有搜索词字典为空，一句 filter 两种场景都能用）
    data_dict = {}
    if search_data:
        # mobile__contains：号码中包含关键词（模糊匹配）
        data_dict["mobile__contains"] = search_data

    # 3. filter(**data_dict)：字典为空时等价于查询全部记录
    #    order_by("-level", "id")：先按级别降序，级别相同时再按 id 升序
    #    （必须排序，否则分页翻页时可能出现数据重复或遗漏）
    queryset = models.PrettyNum.objects.filter(**data_dict).order_by("-level", "id")

    # 4. 对筛选、排序后的结果分页：page_size=2 表示每页 2 条
    page_object = Pagination(request, queryset, page_size=2)

    # 5. 当前页数据、分页条 HTML、搜索关键词一起交给模板
    context = {
        "queryset": page_object.page_queryset,
        "page_string": page_object.html(),
        "search_data": search_data,
    }
    return render(request, "pretty_list.html", context)


def pretty_add(request):
    """ 新建靓号 """
    # GET 请求：只是打开"新建"页面，展示一个空表单
    if request.method == "GET":
        # 不带任何数据 → 得到空表单
        form = PrettyModelForm()
        return render(request, "pretty_add.html", {"form": form})

    # 以下是 POST 请求：用户填好表单并点击了"提交"
    # data=request.POST：把用户提交的数据交给表单做校验
    form = PrettyModelForm(data=request.POST)
    if form.is_valid():
        # 校验通过：直接写库（不带 instance → 新增一条记录）
        form.save()
        # 保存后重定向回列表页（redirect 可避免刷新时重复提交）
        return redirect("/pretty/list/")
    # 校验不通过：把带错误信息的 form 重新渲染，页面会显示红色错误提示
    return render(request, "pretty_add.html", {"form": form})


def pretty_edit(request, nid):
    """ 编辑靓号；nid 是 URL /pretty/<nid>/edit/ 里的那个 ID """
    # 先按 ID 从数据库取出要编辑的那一条对象；取不到时返回 None
    row_object = models.PrettyNum.objects.filter(id=nid).first()

    # GET 请求：打开编辑页，把这条记录的旧数据"回填"到输入框里
    # instance=row_object：告诉表单"要操作的是这一条已有记录"，字段会用它现有值填充
    if request.method == "GET":
        form = PrettyEditModelForm(instance=row_object)
        return render(request, "pretty_edit.html", {"form": form})

    # POST 请求：用户修改后提交
    # 同时带 data（新数据）和 instance（要更新的那条记录）
    form = PrettyEditModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        # 关键点：带 instance 时 save() 是"更新这一条"，不带则是"新增一条"
        form.save()
        return redirect("/pretty/list/")
    # 校验不通过：返回带错误的表单，让用户修改后重新提交
    return render(request, "pretty_edit.html", {"form": form})


def pretty_delete(request, nid):
    """ 删除靓号 """
    # filter(id=nid).delete()：删除 ID 匹配的那条记录（不存在时也不会报错）
    models.PrettyNum.objects.filter(id=nid).delete()
    # 删除后跳回列表页
    return redirect("/pretty/list/")
