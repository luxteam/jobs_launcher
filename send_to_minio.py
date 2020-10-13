import os
import argparse
from ums_client import create_ums_client
from minio_client import create_mc_client
from core.config import *
import glob

res = []
transferred_test_cases = []

ums_client_prod = create_ums_client("PROD")
ums_client_dev = create_ums_client("DEV")
minio_client_prod = None
minio_client_dev = None
if ums_client_prod:
    minio_client_prod = create_mc_client(ums_client_prod.job_id)
if ums_client_dev:
    minio_client_dev = create_mc_client(ums_client_dev.job_id)


def send_to_minio(path, pattern):
    files = glob.glob(pattern)
    for file in files:
        file_path = os.path.join(path, file)
        if ums_client_prod and minio_client_prod:
            minio_client_prod.upload_file(file_path, ums_client_prod.build_id)
        if minio_client_dev and minio_client_dev:
            minio_client_dev.upload_file(file_path, ums_client_dev.build_id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', required=True, type=str, help='path to files')
    parser.add_argument('--pattern', required=True, type=str, help='pattern for files which must be sent')

    args = parser.parse_args()

    send_to_minio(args.path, args.pattern)
