from django import forms

from .bootstrap import bootstrap_form


class BootstrapModelForm(forms.ModelForm):
    """
    带 Bootstrap 样式的 ModelForm 基类。
    子类只需定义 Meta（model + fields），字段样式由基类统一处理，
    避免每个表单都重复写一遍 __init__。
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 借助 bootstrap 工具，给当前表单的所有字段加样式
        bootstrap_form(self.fields)
