# 部门管理视图
from django.shortcuts import render, redirect

from app01 import models
from app01.utils.pagination import Pagination


def depart_list(request):
    """ 部门列表（带分页） """
    # 查出全部部门
    # order_by("id")：指定排序，保证每次分页顺序一致（否则数据库返回顺序不确定，翻页可能漏数据或重复）
    queryset = models.Department.objects.all().order_by("id")
    # 把查询结果交给分页类：page_size=2 表示每页 2 条
    page_object = Pagination(request, queryset, page_size=2)
    context = {
        # 当前页的数据，模板里循环它显示表格
        "queryset": page_object.page_queryset,
        # 分页条 HTML（首页/上一页/页码/下一页/尾页/跳转）
        "page_string": page_object.html(),
    }
    return render(request, "depart_list.html", context)


def depart_add(request):
    """ 新建部门 """
    if request.method == "GET":
        return render(request, "depart_add.html")

    title = request.POST.get("title")
    models.Department.objects.create(title=title)
    return redirect("/depart/list/")


def depart_edit(request, nid):
    """ 编辑部门 """
    row_obj = models.Department.objects.filter(id=nid).first()
    if request.method == "GET":
        return render(request, "depart_edit.html", {"row_obj": row_obj})

    title = request.POST.get("title")
    models.Department.objects.filter(id=nid).update(title=title)
    return redirect("/depart/list/")


def depart_delete(request, nid):
    """ 删除部门 """
    models.Department.objects.filter(id=nid).delete()
    return redirect("/depart/list/")
