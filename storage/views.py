from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import StorageNode, File, FileChunk
from .serializers import StorageNodeSerializer, FileSerializer, FileChunkSerializer
from .services.chunking import FileChunker
from .services.distribution import DistributionService
from .services.storage import MinioStorage
import hashlib


class DashboardView(TemplateView):
    template_name = 'storage/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['files'] = File.objects.filter(owner=self.request.user)
        context['storage_nodes'] = StorageNode.objects.all()
        return context


class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    queryset = File.objects.all()

    def get_queryset(self):
        return File.objects.filter(owner=self.request.user)

    @action(detail=False, methods=['POST'])
    def upload(self, request):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Create file record
        file_instance = File.objects.create(
            name=uploaded_file.name,
            size=uploaded_file.size,
            owner=request.user,
            checksum=hashlib.sha256(uploaded_file.read()).hexdigest()
        )

        # Reset file pointer
        uploaded_file.seek(0)

        # Initialize services
        chunker = FileChunker()
        minio_storage = MinioStorage()

        # Split file into chunks
        chunks = chunker.split_file(uploaded_file)

        # Distribute chunks across nodes
        distributed_chunks = DistributionService.distribute_chunks(file_instance, chunks)

        # Upload chunks to MinIO
        for chunk_record, chunk_data in zip(distributed_chunks, chunks):
            minio_storage.upload_chunk(
                file_instance.file_id,
                chunk_record.chunk_number,
                chunk_data['data']
            )

        return Response(FileSerializer(file_instance).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['GET'])
    def download(self, request, pk=None):
        file_instance = self.get_object()
        minio_storage = MinioStorage()

        # Get all chunks for this file
        chunks = FileChunk.objects.filter(file=file_instance).order_by('chunk_number')

        # Download and merge chunks
        chunk_data = []
        for chunk in chunks:
            data = minio_storage.download_chunk(chunk.path)
            if data is None:
                return Response(
                    {'error': f'Failed to download chunk {chunk.chunk_number}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            chunk_data.append(data)

        # Merge chunks
        chunker = FileChunker()
        complete_file = chunker.merge_chunks(chunk_data)

        # Create response
        response = HttpResponse(complete_file, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_instance.name}"'
        return response


class StorageNodeViewSet(viewsets.ModelViewSet):
    serializer_class = StorageNodeSerializer
    queryset = StorageNode.objects.all()