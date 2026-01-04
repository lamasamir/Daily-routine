# tasks/admin.py - Update to show user info
from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'date', 'is_done', 'created_at')
    list_filter = ('date', 'is_done', 'user')
    search_fields = ('title', 'user__username')
    list_select_related = ('user',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
