from django.contrib import admin

from .models import Category, Expense, ExpenseSplit


class ExpenseSplitInline(admin.TabularInline):
    model = ExpenseSplit
    extra = 1
    autocomplete_fields = ['user']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'amount', 'category', 'paid_by', 'split_type', 'date')
    list_filter = ('split_type', 'category', 'date', 'group')
    search_fields = ('title', 'notes', 'group__name', 'paid_by__username')
    autocomplete_fields = ['group', 'category', 'paid_by', 'created_by']
    date_hierarchy = 'date'
    inlines = [ExpenseSplitInline]


@admin.register(ExpenseSplit)
class ExpenseSplitAdmin(admin.ModelAdmin):
    list_display = ('expense', 'user', 'amount_owed', 'share_value')
    search_fields = ('expense__title', 'user__username')
    autocomplete_fields = ['expense', 'user']