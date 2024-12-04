from django.contrib import admin
from .models import Category, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Sesuaikan dengan field yang ingin Anda tampilkan


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
    'username', 'caption', 'created_at', 'categories','slug')  # Sesuaikan dengan field yang ingin Anda tampilkan
    # Tambahkan 'slug', 'image' jika ingin diperlihatkan juga
