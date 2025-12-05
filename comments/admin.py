from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'product')
    search_fields = ('product__name', 'user__username', 'content')
