"""
S3 Large File Transfer (5GB+) — Same Bucket, Source Path → Local Path
Uses S3 Server-Side Multipart Copy (no download required) for maximum speed.
All data stays in AWS; transfer completes well under 5 minutes for most file sizes.
"""

import boto3
import math
import time
import logging
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from botocore.config import Config

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────
PART_SIZE_BYTES   = 512 * 1024 * 1024   # 512 MB per part (AWS max = 5 GB, min = 5 MB)
MAX_WORKERS       = 10                  # parallel part-copy threads
MAX_POOL_CONN     = 50                  # boto3 connection pool size
BOTO3_RETRIES     = 5                   # automatic SDK retries per call


# ── S3 client factory ─────────────────────────────────────────────────────────
def make_client(region: str | None = None) -> boto3.client:
    cfg = Config(
        retries={"max_attempts": BOTO3_RETRIES, "mode": "adaptive"},
        max_pool_connections=MAX_POOL_CONN,
    )
    kwargs = {"config": cfg}
    if region:
        kwargs["region_name"] = region
    return boto3.client("s3", **kwargs)


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_object_size(client, bucket: str, key: str) -> int:
    resp = client.head_object(Bucket=bucket, Key=key)
    return resp["ContentLength"]


def copy_part(client, bucket, src_key, dst_key, upload_id,
              part_number, byte_start, byte_end) -> dict:
    """Copy a single byte range; returns the ETag dict needed for completion."""
    byte_range = f"bytes={byte_start}-{byte_end}"
    resp = client.upload_part_copy(
        Bucket=bucket,
        Key=dst_key,
        CopySource={"Bucket": bucket, "Key": src_key},
        CopySourceRange=byte_range,
        UploadId=upload_id,
        PartNumber=part_number,
    )
    etag = resp["CopyPartResult"]["ETag"]
    log.info("  ✓ Part %3d  range %-35s  ETag %s", part_number, byte_range, etag)
    return {"PartNumber": part_number, "ETag": etag}


# ── Core transfer ─────────────────────────────────────────────────────────────
def transfer(
    bucket: str,
    source_key: str,
    dest_key: str,
    region: str | None = None,
    part_size: int = PART_SIZE_BYTES,
    max_workers: int = MAX_WORKERS,
) -> None:
    client = make_client(region)

    # ── Validate source ───────────────────────────────────────────────────────
    log.info("Inspecting source  s3://%s/%s", bucket, source_key)
    file_size = get_object_size(client, bucket, source_key)
    log.info("File size : %s GB  (%.0f bytes)",
             f"{file_size / 1e9:.2f}", file_size)

    if source_key == dest_key:
        raise ValueError("source_key and dest_key must be different.")

    # ── Calculate parts ───────────────────────────────────────────────────────
    num_parts = math.ceil(file_size / part_size)
    log.info("Strategy  : multipart server-side copy  |  %d parts × ~%d MB",
             num_parts, part_size // 1024 // 1024)

    # ── Initiate multipart upload ─────────────────────────────────────────────
    mpu = client.create_multipart_upload(Bucket=bucket, Key=dest_key)
    upload_id = mpu["UploadId"]
    log.info("Upload ID : %s", upload_id)

    parts: list[dict] = []
    t0 = time.perf_counter()

    try:
        futures = {}
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            for part_num in range(1, num_parts + 1):
                byte_start = (part_num - 1) * part_size
                byte_end   = min(part_num * part_size, file_size) - 1
                fut = pool.submit(
                    copy_part,
                    client, bucket, source_key, dest_key,
                    upload_id, part_num, byte_start, byte_end,
                )
                futures[fut] = part_num

            for fut in as_completed(futures):
                parts.append(fut.result())   # raises if the thread raised

        # Sort by PartNumber before completing
        parts.sort(key=lambda p: p["PartNumber"])

        # ── Complete multipart upload ─────────────────────────────────────────
        client.complete_multipart_upload(
            Bucket=bucket,
            Key=dest_key,
            UploadId=upload_id,
            MultipartUpload={"Parts": parts},
        )

    except Exception:
        log.error("Error — aborting multipart upload %s", upload_id)
        client.abort_multipart_upload(
            Bucket=bucket, Key=dest_key, UploadId=upload_id
        )
        raise

    elapsed   = time.perf_counter() - t0
    speed_gbs = (file_size / elapsed) / 1e9

    log.info("─" * 60)
    log.info("Transfer complete!")
    log.info("  Destination : s3://%s/%s", bucket, dest_key)
    log.info("  Elapsed     : %.1f s  (%.2f min)", elapsed, elapsed / 60)
    log.info("  Throughput  : %.2f GB/s  (server-side)", speed_gbs)
    log.info("─" * 60)


# ── CLI ───────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(
        description="High-speed S3 same-bucket large-file copy (server-side multipart)."
    )
    p.add_argument("--bucket",      required=True, help="S3 bucket name")
    p.add_argument("--source-key",  required=True, help="Source object key  (e.g. data/raw/big.bin)")
    p.add_argument("--dest-key",    required=True, help="Destination key    (e.g. data/local/big.bin)")
    p.add_argument("--region",      default=None,  help="AWS region (optional; uses env/config if omitted)")
    p.add_argument("--part-size-mb",type=int, default=512,
                   help="Part size in MB (default 512; min 5, max 5120)")
    p.add_argument("--workers",     type=int, default=MAX_WORKERS,
                   help=f"Parallel copy threads (default {MAX_WORKERS})")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    part_size = args.part_size_mb * 1024 * 1024
    if not (5 * 1024 * 1024 <= part_size <= 5 * 1024 * 1024 * 1024):
        raise ValueError("--part-size-mb must be between 5 and 5120.")

    transfer(
        bucket     = args.bucket,
        source_key = args.source_key,
        dest_key   = args.dest_key,
        region     = args.region,
        part_size  = part_size,
        max_workers= args.workers,
    )
