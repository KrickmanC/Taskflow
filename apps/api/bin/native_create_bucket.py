#!/usr/bin/env python3
import os
import time

import boto3
from botocore.exceptions import ClientError, EndpointConnectionError


def main() -> None:
    endpoint_url = os.environ["AWS_S3_ENDPOINT_URL"]
    access_key = os.environ["AWS_ACCESS_KEY_ID"]
    secret_key = os.environ["AWS_SECRET_ACCESS_KEY"]
    bucket_name = os.environ.get("AWS_S3_BUCKET_NAME", "uploads")
    region = os.environ.get("AWS_REGION") or "us-east-1"

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )

    for attempt in range(1, 31):
        try:
            s3.head_bucket(Bucket=bucket_name)
            print(f"Bucket already exists: {bucket_name}")
            return
        except EndpointConnectionError:
            if attempt == 30:
                raise
            time.sleep(2)
        except ClientError:
            break

    s3.create_bucket(Bucket=bucket_name)
    print(f"Bucket created: {bucket_name}")


if __name__ == "__main__":
    main()
