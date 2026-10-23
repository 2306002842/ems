# 联通用户管理系统（EMS）项目总结

## 1. 项目简介

基于 **Django 6.1 + MySQL** 的后台管理项目，包含部门、用户、靓号三个管理模块。

- 前端：Bootstrap 3.4.1 + jQuery，模板统一继承 `layout.html`
- 语言/时区：`zh-hans`、`Asia/Shanghai`
- 三个列表页均支持分页，用户与靓号列表支持关键词搜索

## 2. 功能模块

### 部门管理
- 部门列表（分页）
- 新建、编辑、删除部门
- 字段：标题

### 用户管理
- 用户列表（按手机号模糊搜索、分页）
- 手动表单新增用户
- ModelForm 新增用户（用户名至少 3 个字符）
- 编辑、删除用户
- 字段：姓名、密码、年龄、账户余额、手机号、入职时间、部门、性别

### 靓号管理
- 靓号列表（按号码模糊搜索、按级别排序、分页）
- 新建、编辑、删除靓号
- 编辑时校验：
  - 号码必须为 11 位手机号（`^1[3-9]\d{9}$`）
  - 号码不能与其他记录重复（排除自身）

## 3. 目录结构

```text
ems/
├── manage.py
├── ems/                          # 项目配置
│   ├── settings.py
│   ├── local_settings.py         # 本地数据库密码（不提交 Git）
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── app01/                        # 业务应用
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py                 # 数据模型
    ├── migrations/               # 数据库迁移文件
    ├── static/                   # 静态资源（Bootstrap、jQuery 等）
    ├── templates/
    │   ├── layout.html           # 母版：导航栏 + 公共脚本
    │   ├── depart_list.html
    │   ├── depart_add.html
    │   ├── depart_edit.html
    │   ├── user_list.html
    │   ├── user_add.html
    │   ├── user_model_form_add.html
    │   ├── user_edit.html
    │   ├── pretty_list.html
    │   ├── pretty_add.html
    │   └── pretty_edit.html
    ├── utils/                    # 通用工具
    │   ├── __init__.py
    │   ├── bootstrap.py          # 表单控件统一样式
    │   ├── form.py               # BootstrapModelForm 基类
    │   └── pagination.py         # Pagination 分页类
    └── views/                    # 视图（按模块拆分）
        ├── __init__.py           # 统一导出视图函数
        ├── depart.py             # 部门管理
        ├── user.py               # 用户管理
        └── pretty.py             # 靓号管理
```

`views/__init__.py` 负责把三个子模块的视图函数导出，因此 `ems/urls.py` 中依然可以统一写成 `views.depart_list`、`views.user_list` 等。

## 4. 数据模型

| 模型 | 说明 | 主要字段 |
| --- | --- | --- |
| `Department` | 部门表 | `title`（标题） |
| `UserInfo` | 员工表 | `name`、`password`、`age`、`account`、`phone`、`create_time`、`depart`（外键）、`gender` |
| `PrettyNum` | 靓号表 | `mobile`（号码）、`price`（价格）、`level`（1级/2级）、`status`（已占用/未占用） |

`UserInfo.depart` 通过外键关联 `Department`，数据库列名为 `depart_id`。

## 5. 路由一览

| 路径 | 视图 | 说明 |
| --- | --- | --- |
| `/` | `depart_list` | 首页跳转部门列表 |
| `/depart/list/` | `depart_list` | 部门列表 |
| `/depart/add/` | `depart_add` | 新建部门 |
| `/depart/<id>/edit/` | `depart_edit` | 编辑部门 |
| `/depart/<id>/delete/` | `depart_delete` | 删除部门 |
| `/user/list/` | `user_list` | 用户列表（支持 `?q=手机号`） |
| `/user/add/` | `user_add` | 手动表单新建用户 |
| `/user/modelform/add/` | `user_model_form_add` | ModelForm 新建用户 |
| `/user/<id>/edit/` | `user_edit` | 编辑用户 |
| `/user/<id>/delete/` | `user_delete` | 删除用户 |
| `/pretty/list/` | `pretty_list` | 靓号列表（支持 `?q=号码`） |
| `/pretty/add/` | `pretty_add` | 新建靓号 |
| `/pretty/<id>/edit/` | `pretty_edit` | 编辑靓号 |
| `/pretty/<id>/delete/` | `pretty_delete` | 删除靓号 |

## 6. 核心实现说明

### 6.1 分页

`app01/utils/pagination.py` 中的 `Pagination` 类负责分页：

```python
page_object = Pagination(request, queryset, page_size=2)
context = {
    "queryset": page_object.page_queryset,  # 当前页数据
    "page_string": page_object.html(),      # 分页条 HTML
}
```

- `page_queryset`：当前页的数据切片，模板直接循环
- `html()`：生成首页 / 上一页 / 页码 / 下一页 / 尾页 / 页码跳转
- 页码只显示当前页前后各 5 页，避免页数过多撑开页面
- 自动保留 `q` 等查询参数，翻页或跳转时不会丢失搜索条件
- 页码非法或越界时自动回退到第 1 页或最后一页

### 6.2 表单样式复用

- `utils/bootstrap.py` 的 `bootstrap_form(fields)`：给所有字段统一加 `form-control` 和 `placeholder`
- `utils/form.py` 的 `BootstrapModelForm`：继承 `forms.ModelForm`，在 `__init__` 中调用上述方法
- `UserModelForm`、`PrettyModelForm`、`PrettyEditModelForm` 都继承该基类，子类只需写 `Meta`

### 6.3 搜索

用户列表与靓号列表使用 GET 参数 `q`：

```python
data_dict = {}
if search_data:
    data_dict["phone__contains"] = search_data   # 用户：按手机号
    # data_dict["mobile__contains"] = search_data  # 靓号：按号码
queryset = models.UserInfo.objects.filter(**data_dict)
```

字典为空时等价于查询全部记录；有搜索词时做模糊匹配。

### 6.4 新增与编辑的区别

- `form = XxxModelForm(data=request.POST)`：不带 `instance`，`save()` 为**新增**
- `form = XxxModelForm(data=request.POST, instance=row_object)`：带 `instance`，`save()` 为**更新该条记录**

### 6.5 视图的 GET / POST 分支

同一个视图同时处理两种请求：

- `GET`：只渲染页面（空表单或回填已有数据）
- `POST`：校验表单并保存，成功后 `redirect` 回列表页，避免刷新重复提交

## 7. 运行方式

1. 安装依赖：

```bash
pip install django mysqlclient
```

2. 在 MySQL 中创建数据库（字符集建议 `utf8mb4`）：

```sql
CREATE DATABASE ems DEFAULT CHARACTER SET utf8mb4;
```

3. 创建 `ems/local_settings.py`，填入本机数据库配置（该文件已被 `.gitignore` 忽略，不会提交）：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ems',
        'USER': 'root',
        'PASSWORD': '你的数据库密码',
        'HOST': '127.0.0.1',
        'PORT': 3306,
    }
}
```

`ems/settings.py` 末尾会自动导入该文件；没有这个文件时使用空密码配置。

4. 执行迁移并启动：

```bash
python manage.py migrate
python manage.py runserver
```

5. 浏览器访问：

- 部门管理：http://localhost:8000/depart/list/
- 用户管理：http://localhost:8000/user/list/
- 靓号管理：http://localhost:8000/pretty/list/

## 8. 注意事项

- 三个列表页当前 `page_size=2`，仅用于演示分页效果；实际使用可在 `views/depart.py`、`views/user.py`、`views/pretty.py` 中调整。
- 现有靓号测试数据（如 `123456`、`999999999`）不是合法的 11 位手机号，编辑时必须改成 `1[3-9]` 开头的 11 位号码才能保存。
- 数据库账号密码只写在本地 `ems/local_settings.py` 中，该文件已被 `.gitignore` 忽略；`settings.py` 本身不包含密码。
- 用户与靓号的搜索条件通过 URL 参数 `q` 传递，例如 `/user/list/?q=139`。

## 9. 验证结果

- `python manage.py check`：无问题
- 部门、用户、靓号的列表页与新建/编辑页均正常返回 200
- 分页：页码高亮、首页/尾页、越界页码回退、翻页保留搜索条件均正常
- 靓号编辑：号码格式错误提示、重复号码提示、正常保存跳转均正常
