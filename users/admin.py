from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('age', 'gender')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('age', 'gender')}),
    )
    list_display = ('username', 'email', 'age', 'gender', 'is_staff', 'created_at')
    list_filter = BaseUserAdmin.list_filter + ('gender', 'age', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')