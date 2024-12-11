from django.contrib import admin
from .models import Category, Post,User,Profile,Comments,Follow
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserAdmin(BaseUserAdmin):
    ordering = ['email']
    list_display = ['email', 'name','is_staff']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name','profile_picture','bio','linkedin')}),
        (
            'Permissions',
            {
                'fields': (
                    'groups',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        )
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name','email', 'password1', 'password2')
        }),
    )

admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Profile)
admin.site.register(Comments)
admin.site.register(Follow)
admin.site.register(User,UserAdmin)