from storages.backends.s3boto3 import S3Boto3Storage

def salvar_arquivo_com_acl(path, content):
    storage = S3Boto3Storage()
    saved_path = storage.save(path, content)

    # ACL pública
    storage.connection.meta.client.put_object_acl(
        ACL='public-read',
        Bucket=storage.bucket_name,
        Key=storage._normalize_name(saved_path),  # `_clean_name` não é mais necessário
    )

    return storage.url(saved_path)