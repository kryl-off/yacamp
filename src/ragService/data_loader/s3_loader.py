import boto3
import tempfile
import os
from typing import List, Tuple

from src.ragService.config.settings import S3Config, RetrieverConfig

def download_from_s3() -> Tuple[List[str], List[str]]:
    s3 = boto3.client(
        's3',
        endpoint_url=S3Config.ENDPOINT,
        aws_access_key_id=S3Config.ACCESS_KEY,
        aws_secret_access_key=S3Config.SECRET_KEY,
    )

    successful_downloads = []
    failed_downloads = []

    try:
        objects = s3.list_objects_v2(Bucket=S3Config.BUCKET, Prefix=S3Config.PREFIX)
    except Exception as e:
        raise ConnectionError(f"Ошибка подключения к S3: {e}")

    if 'Contents' not in objects:
        return [], ["No objects found in bucket"]

    with tempfile.TemporaryDirectory() as tmpdir:
        for obj in objects['Contents']:
            key = obj.get('Key')
            if not key or not isinstance(key, str) or key.endswith('/'):
                continue

            size = obj.get('Size', 0)
            if size == 0 or size > RetrieverConfig.MAX_FILE_SIZE:
                failed_downloads.append(f"{key}: Invalid size")
                continue

            local_path = os.path.join(tmpdir, os.path.basename(key))
            try:
                s3.download_file(S3Config.BUCKET, key, local_path)

                # Проверка целостности файла
                if os.path.getsize(local_path) != size:
                    os.remove(local_path)
                    failed_downloads.append(f"{key}: Size mismatch after download")
                    continue

                successful_downloads.append(local_path)
            except Exception as e:
                failed_downloads.append(f"{key}: {str(e)}")
                continue

    return successful_downloads, failed_downloads