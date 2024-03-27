from django.contrib import admin
from . import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
# Define custom permission




@admin.register(models.UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'mobile_phone')
    search_fields = ('username', 'email', 'mobile_phone')


@admin.register(models.PricePolicy)
class PricePolicyAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'project_num', 'project_member', 'project_space', 'per_file_size')
    list_filter = ('category',)
    search_fields = ('title',)

@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'status', 'price', 'start_datetime', 'end_datetime')
    list_filter = ('status',)
    search_fields = ('order', 'user__username')

@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'create_datetime', 'join_count')
    search_fields = ('name', 'creator__username')

@admin.register(models.ProjectUser)
class ProjectUserAdmin(admin.ModelAdmin):
    list_display = ('project', 'get_username', 'create_datetime')  # 使用get_username方法获取关联用户的用户名
    search_fields = ('project__name', 'user__username')

    def get_username(self, obj):
        return obj.user.username  # 获取关联用户的用户名
    get_username.short_description = 'User'  # 设置列的标题为'User'

@admin.register(models.Wiki)
class WikiAdmin(admin.ModelAdmin):
    list_display = ('project', 'title', 'depth')
    search_fields = ('project__name', 'title')

@admin.register(models.FileRepository)
class FileRepositoryAdmin(admin.ModelAdmin):
    list_display = ('project', 'name', 'file_type', 'file_size', 'update_user', 'update_datetime')
    search_fields = ('project__name', 'name')

@admin.register(models.Issues)
class IssuesAdmin(admin.ModelAdmin):
    list_display = ('project', 'subject', 'status', 'priority', 'creator', 'create_datetime')
    list_filter = ('status', 'priority')
    search_fields = ('project__name', 'subject', 'creator__username')

@admin.register(models.Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('get_projectname', 'title')
    search_fields = ('project__name', 'title')
    def get_projectname(self, obj):
        return obj.project.name
    get_projectname.short_description = 'project'

@admin.register(models.IssuesType)
class IssuesTypeAdmin(admin.ModelAdmin):
    list_display = ('title', 'project')
    search_fields = ('title', 'project__name')

@admin.register(models.IssuesReply)
class IssuesReplyAdmin(admin.ModelAdmin):
    list_display = ('issues', 'content', 'creator', 'create_datetime')
    search_fields = ('issues__subject', 'creator__username')

@admin.register(models.ProjectInvite)
class ProjectInviteAdmin(admin.ModelAdmin):
    list_display = ('project', 'code', 'count', 'use_count', 'period', 'creator', 'create_datetime')
    search_fields = ('project__name', 'code', 'creator__username')
