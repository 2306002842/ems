# views 包入口：把三个子模块中的视图函数统一导出
# 这样 ems/urls.py 里继续写 views.depart_list、views.user_list 等即可，无需改动路由
from .depart import depart_list, depart_add, depart_edit, depart_delete
from .user import user_list, user_add, user_model_form_add, user_delete, user_edit
from .pretty import pretty_list, pretty_add, pretty_edit, pretty_delete
