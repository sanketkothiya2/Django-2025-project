from ..models import StorageNode, FileChunk
from django.db.models import Count


class DistributionService:
    @staticmethod
    def get_least_loaded_node():
        return StorageNode.objects.filter(
            status='ACTIVE'
        ).annotate(
            chunk_count=Count('filechunk')
        ).order_by('chunk_count').first()

    @staticmethod
    def get_nearest_node(user_location=None):
        # Simplified version - returns least loaded node
        # In a real implementation, you would compare node locations with user_location
        return DistributionService.get_least_loaded_node()

    @staticmethod
    def distribute_chunks(file, chunks):
        distributed_chunks = []
        for chunk_number, chunk in enumerate(chunks):
            # Get least loaded node
            node = DistributionService.get_least_loaded_node()

            # Create file chunk record
            chunk_record = FileChunk.objects.create(
                file=file,
                node=node,
                chunk_number=chunk_number,
                size=chunk['size'],
                checksum=chunk['checksum'],
                path=f"{file.file_id}/{chunk_number}"
            )
            distributed_chunks.append(chunk_record)

        return distributed_chunks