from django.db import models
from django.contrib.auth.models import User
import uuid

class StorageNode(models.Model):
    node_id = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=[
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('MAINTENANCE', 'Maintenance')
    ])
    storage_capacity = models.BigIntegerField()  # in bytes
    used_storage = models.BigIntegerField(default=0)  # in bytes

    def __str__(self):
        return f"{self.name} ({self.address})"

class File(models.Model):
    file_id = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    size = models.BigIntegerField()  # in bytes
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    checksum = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class FileChunk(models.Model):
    chunk_id = models.UUIDField(default=uuid.uuid4, editable=False)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    node = models.ForeignKey(StorageNode, on_delete=models.CASCADE)
    chunk_number = models.IntegerField()
    size = models.BigIntegerField()  # in bytes
    checksum = models.CharField(max_length=64)
    path = models.CharField(max_length=255)

    class Meta:
        unique_together = ('file', 'chunk_number', 'node')