"""Download binary metadata or perform an explicitly confirmed upload."""

import argparse
import os
from pathlib import Path

from bcic import Client


def main() -> None:
    """Run a bounded download; upload only when explicitly confirmed."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload", type=Path)
    parser.add_argument("--confirm-upload", action="store_true")
    args = parser.parse_args()
    object_name = os.environ.get("BCIC_EXAMPLE_OBJECT", "Contact")
    record_id = os.environ.get("BCIC_EXAMPLE_RECORD_ID", "RECORD_ID")
    field_name = os.environ.get("BCIC_EXAMPLE_BINARY_FIELD", "Attachment")

    with Client.from_env() as client:
        if args.upload is None:
            result = client.binary.get(
                object_name, record_id, field_name, max_bytes=1_048_576
            )
            print(result.metadata.file_name, result.metadata.size)
            return
        if not args.confirm_upload:
            raise SystemExit("Pass --confirm-upload to perform the upload")
        content = args.upload.read_bytes()
        result = client.binary.set(
            object_name,
            record_id,
            field_name,
            content,
            file_name=args.upload.name,
            content_type="application/octet-stream",
            max_bytes=1_048_576,
        )
        print(result.status)


if __name__ == "__main__":
    main()
