from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', '管理员'),
        ('receptionist', '前台接件员'),
        ('technician', '维修技师'),
        ('cashier', '收银员'),
    )
    
    phone = models.CharField('联系电话', max_length=20, blank=True)
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default='receptionist')
    employee_id = models.CharField('工号', max_length=50, unique=True, blank=True, null=True)

    class Meta:
        db_table = 'tf_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.get_role_display()} - {self.username}'
