from rest_framework import serializers
from .models import StorageNode, File, FileChunk

class StorageNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageNode
        fields = '__all__'

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'
        read_only_fields = ('file_id', 'owner', 'created_at', 'updated_at')

class FileChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileChunk
        fields = '__all__'
        read_only_fields = ('chunk_id',)