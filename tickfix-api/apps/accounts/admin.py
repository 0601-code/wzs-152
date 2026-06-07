from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'employee_id', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'phone', 'employee_id')
    fieldsets = UserAdmin.fieldsets + (
        ('额外信息', {'fields': ('phone', 'role', 'employee_id')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('额外信息', {'fields': ('phone', 'role', 'employee_id')}),
    )
