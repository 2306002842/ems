from django.db import models


class Department(models.Model):
    """ 部门表 """
    title = models.CharField(verbose_name='标题', max_length=32)

    def __str__(self):
        return self.title


class UserInfo(models.Model):
    """ 员工表 """
    name = models.CharField(verbose_name="姓名", max_length=32)
    password = models.CharField(verbose_name="密码", max_length=64)
    age = models.IntegerField(verbose_name="年龄", default=2)
    account = models.CharField(verbose_name="账户余额", max_length=16, default="100000")
    phone = models.CharField(verbose_name="手机号", max_length=11, null=True, blank=True)
    create_time = models.DateField(verbose_name="入职时间")
    # 外键：关联部门表，depart_id 对应 Department 的 id
    depart = models.ForeignKey(
        verbose_name="部门",
        to="Department",
        to_field="id",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column="depart_id",
    )
    gender_choices = (
        (1, "男"),
        (2, "女"),
    )
    gender = models.SmallIntegerField(verbose_name="性别", choices=gender_choices, null=True, blank=True)


class PrettyNum(models.Model):
    """ 靓号表 """
    mobile = models.CharField(verbose_name="号码", max_length=11)
    price = models.IntegerField(verbose_name="价格", default=0)

    level_choices = (
        (1, "1级"),
        (2, "2级"),
    )
    level = models.SmallIntegerField(verbose_name="级别", choices=level_choices, default=1)

    status_choices = (
        (1, "已占用"),
        (2, "未占用"),
    )
    status = models.SmallIntegerField(verbose_name="状态", choices=status_choices, default=2)