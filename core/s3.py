import os

import boto3
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "bot-translations")

# Command to check files in bucket:
# aws s3 ls s3://meeting-bot --recursive --endpoint-url http://localhost:8080 --no-sign-request

# Command to delete single file in bucket:
# aws s3 rm s3://meeting-bot/2024-06-17T12:00:00Z.json --endpoint-url http://localhost:8080 --no-sign-request


def get_s3_client():
    endpoint_url = os.getenv("S3_ENDPOINT_URL")

    kwargs = {
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID", "local"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY", "local"),
        "region_name": os.getenv("AWS_REGION", "us-east-1"),
    }

    if endpoint_url:
        # Local S3 requires path-style addressing
        kwargs["endpoint_url"] = endpoint_url
        kwargs["config"] = Config(s3={"addressing_style": "path"})

    return boto3.client("s3", **kwargs)


PRESIGNED_URL_EXPIRY = int(os.getenv("PRESIGNED_URL_EXPIRY", "3600"))


def generate_presigned_url(s3_client, bucket: str, key: str) -> str:
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=PRESIGNED_URL_EXPIRY,
    )


def ensure_bucket_exists(s3_client) -> None:
    """Create the bucket if it doesn't exist (useful for local development)."""
    existing = [b["Name"] for b in s3_client.list_buckets().get("Buckets", [])]
    if BUCKET_NAME not in existing:
        s3_client.create_bucket(Bucket=BUCKET_NAME)
