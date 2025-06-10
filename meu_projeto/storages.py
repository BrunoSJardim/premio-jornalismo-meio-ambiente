from storages.backends.s3boto3 import S3Boto3Storage

class PublicMediaStorage(S3Boto3Storage):
    default_acl = 'public-read'
    querystring_auth = False

    def _save(self, name, content):
        content.seek(0)  # Garante leitura do início
        name = super()._save(name, content)

        print(f"Aplicando ACL public-read ao objeto: {name}")  # <-- aparecerá no log

        self.connection.meta.client.put_object_acl(
            ACL='public-read',
            Bucket=self.bucket_name,
            Key=self._normalize_name(self._clean_name(name)),
        )
        return name