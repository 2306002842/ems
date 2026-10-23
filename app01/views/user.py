# 用户管理视图
from django.shortcuts import render, redirect
from django import forms

from app01 import models
from app01.utils.form import BootstrapModelForm
from app01.utils.pagination import Pagination


def user_list(request):
    """ 用户列表 """
    # 获取搜索关键词（按手机号搜索）
    search_data = request.GET.get("q", "")
    data_dict = {}
    if search_data:
        data_dict["phone__contains"] = search_data
    # order_by("id")：分页前必须先排序，否则翻页结果可能不稳定
    queryset = models.UserInfo.objects.filter(**data_dict).order_by("id")

    # 对“筛选后的结果”分页：page_size=2 表示每页 2 条
    page_object = Pagination(request, queryset, page_size=2)

    # search_data 传给模板回填搜索框；分页类会自动保留 q 参数，翻页不丢搜索条件
    context = {
        "queryset": page_object.page_queryset,
        "page_string": page_object.html(),
        "search_data": search_data,
    }
    return render(request, "user_list.html", context)


def user_add(request):
    """ 添加用户 """
    if request.method == "GET":
        context = {
            "gender_choices": models.UserInfo.gender_choices,
            "depart_list": models.Department.objects.all(),
        }
        return render(request, "user_add.html", context)

    models.UserInfo.objects.create(
        name=request.POST.get("name"),
        password=request.POST.get("password"),
        age=request.POST.get("age"),
        account=request.POST.get("account"),
        phone=request.POST.get("phone"),
        create_time=request.POST.get("create_time"),
        depart_id=request.POST.get("depart"),
        gender=request.POST.get("gender"),
    )
    return redirect("/user/list/")


class UserModelForm(BootstrapModelForm):
    name = forms.CharField(min_length=3, label="用户名")

    class Meta:
        model = models.UserInfo
        fields = ["name", "password", "age", "account", "phone", "create_time", "gender", "depart"]


def user_model_form_add(request):
    """ 添加用户（ModelForm） """
    if request.method == "GET":
        form = UserModelForm()
        return render(request, "user_model_form_add.html", {"form": form})

    form = UserModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect("/user/list/")
    return render(request, "user_model_form_add.html", {"form": form})


def user_delete(request, nid):
    """ 删除用户 """
    models.UserInfo.objects.filter(id=nid).delete()
    return redirect("/user/list/")


def user_edit(request, nid):
    """ 编辑用户 """
    # 根据id获取某一行对象
    row_object = models.UserInfo.objects.filter(id=nid).first()

    if request.method == "GET":
        # 根据ID去数据库获取要编辑的那一行数据（对象）显示在输入框中
        form = UserModelForm(instance=row_object)
        return render(request, "user_edit.html", {"form": form})

    # instance=row_object 代表更新到某一行，不然 form.save() 会单独加一条数据
    form = UserModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect("/user/list/")
    return render(request, "user_edit.html", {"form": form})
