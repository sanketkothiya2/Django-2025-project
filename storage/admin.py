from django.contrib import admin
from .models import StorageNode, File, FileChunk

@admin.register(StorageNode)
class StorageNodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'status', 'storage_capacity', 'used_storage')
    list_filter = ('status',)
    search_fields = ('name', 'address')

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'size', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'owner__username')

@admin.register(FileChunk)
class FileChunkAdmin(admin.ModelAdmin):
    list_display = ('file', 'node', 'chunk_number', 'size')
    list_filter = ('node',)
    search_fields = ('file__name', 'node__name')