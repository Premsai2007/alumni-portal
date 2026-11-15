from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Profile
from .models import Announcement
admin.site.register(Announcement)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_verified', 'batch_year', 'department', 'company')
    list_filter = ('role', 'is_verified', 'department')
    search_fields = ('user__username', 'user__email', 'company')
    actions = ['approve_selected']

    @admin.action(description='Approve selected alumni')
    def approve_selected(self, request, queryset):
        count = queryset.filter(role='alumni').update(is_verified=True)
        self.message_user(request, f'{count} alumni approved.')