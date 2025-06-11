from storages.backends.s3boto3 import S3Boto3Storage

def salvar_arquivo(path, content):
    storage = S3Boto3Storage()
    saved_path = storage.save(path, content)
    return storage.url(saved_path)