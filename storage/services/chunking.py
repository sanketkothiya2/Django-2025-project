import hashlib

class FileChunker:
    def __init__(self, chunk_size=5*1024*1024):  # 5MB default chunk size
        self.chunk_size = chunk_size

    def split_file(self, file):
        chunks = []
        while True:
            chunk = file.read(self.chunk_size)
            if not chunk:
                break
            chunks.append({
                'data': chunk,
                'size': len(chunk),
                'checksum': hashlib.sha256(chunk).hexdigest()
            })
        return chunks

    def merge_chunks(self, chunks):
        return b''.join(chunks)