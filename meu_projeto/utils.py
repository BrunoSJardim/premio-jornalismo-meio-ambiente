from django.core.files.storage import default_storage

def salvar_arquivo_com_acl(path, content):

    # Salva o arquivo usando o storage padrão (S3)

    saved_path = default_storage.save(path, content)

    # Aplica ACL public-read após o upload

    default_storage.connection.meta.client.put_object_acl(
        ACL='public-read',
        Bucket=default_storage.bucket_name,
        Key=default_storage._normalize_name(default_storage._clean_name(saved_path)),
    )

    # Retorna a URL final do arquivo no S3
    
    return default_storage.url(saved_path)