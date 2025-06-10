from storages.backends.s3boto3 import S3Boto3Storage

def salvar_arquivo_com_acl(path, content):
    storage = S3Boto3Storage()
    saved_path = storage.save(path, content)

    # Aplica ACL public-read após o upload
    storage.connection.meta.client.put_object_acl(
        ACL='public-read',
        Bucket=storage.bucket_name,
        Key=storage._normalize_name(storage._clean_name(saved_path)),
    )

    return storage.url(saved_path)