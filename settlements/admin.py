from django.contrib import admin

from .models import Settlement


@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = ('group', 'paid_by', 'paid_to', 'amount', 'status', 'settled_at', 'created_at')
    list_filter = ('status', 'group', 'created_at')
    search_fields = ('group__name', 'paid_by__username', 'paid_to__username')
    autocomplete_fields = ['group', 'paid_by', 'paid_to']
    actions = ['mark_completed']

    @admin.action(description="Mark selected settlements as completed")
    def mark_completed(self, request, queryset):
        for settlement in queryset:
            settlement.mark_completed()