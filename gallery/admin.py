from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_name_zh', 'category_name_en', 'parent', 'level', 'is_last_level', 'status', 'rank_id')
    list_filter = ('level', 'is_last_level', 'status')
    search_fields = ('category_name_zh', 'category_name_en')
    ordering = ('rank_id', 'id')
