import os

import boto3
from dotenv import load_dotenv

load_dotenv()

BEDROCK_REGION = os.getenv("AWS_BEDROCK_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001")
BEDROCK_MAX_TOKENS = int(os.getenv("BEDROCK_MAX_TOKENS", "8192"))


def get_bedrock_client():
    kwargs = {
        "region_name": BEDROCK_REGION,
    }

    access_key = os.getenv("AWS_BEDROCK_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_BEDROCK_SECRET_ACCESS_KEY")
    if access_key and secret_key:
        kwargs["aws_access_key_id"] = access_key
        kwargs["aws_secret_access_key"] = secret_key

    return boto3.client("bedrock-runtime", **kwargs)
