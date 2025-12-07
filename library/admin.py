from django.contrib import admin
from .models import Author, Material, MaterialAccess


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'subject',
        'material_type',
        'authors_display',
        'publication_year',
        'is_active',
        'view_count',
        'download_count',
        'created_at'
    )
    search_fields = ('title', 'isbn', 'publisher')
    list_filter = ('material_type', 'subject', 'language', 'is_active')
    filter_horizontal = ('authors',)
    readonly_fields = ('view_count', 'download_count', 'created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(MaterialAccess)
class MaterialAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'material', 'action', 'ip_address', 'accessed_at')
    search_fields = ('user__username', 'material__title', 'ip_address')
    list_filter = ('action', 'accessed_at')
    ordering = ('-accessed_at',)
