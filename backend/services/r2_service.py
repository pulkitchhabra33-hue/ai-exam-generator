import os

import boto3
from botocore.client import Config

# ============================================================
# CLOUDFLARE R2 CONFIGURATION
# ============================================================

R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")


R2_ENDPOINT = (
    f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
)


# ============================================================
# R2 CLIENT
# ============================================================

r2_client = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name="auto",
    config=Config(
        signature_version="s3v4"
    )
)


# ============================================================
# UPLOAD PDF
# ============================================================

def upload_pdf(
    local_file_path: str,
    object_key: str
):

    r2_client.upload_file(
        local_file_path,
        R2_BUCKET_NAME,
        object_key,
        ExtraArgs={
            "ContentType": "application/pdf"
        }
    )

    return object_key


# ============================================================
# GENERATE DOWNLOAD URL
# ============================================================

def generate_download_url(
    object_key: str,
    expires_in: int = 3600
):

    url = r2_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": R2_BUCKET_NAME,
            "Key": object_key
        },
        ExpiresIn=expires_in
    )

    return url