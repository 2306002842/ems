def bootstrap_form(fields):
    """
    给表单的所有字段统一加上 Bootstrap 样式。
    fields：form.fields（字典，键是字段名，值是字段对象）

    做了两件事：
    1. class="form-control"：套用 Bootstrap 的输入框样式
    2. placeholder=field.label：把字段标题（verbose_name）作为灰色提示文字
    """
    for field in fields.values():
        field.widget.attrs = {"class": "form-control", "placeholder": field.label}
