"""Retrieve one typed BCIC record."""

import os

from bcic import Client


def main() -> None:
    """Read a record identified by environment-provided non-secret IDs."""
    object_name = os.environ.get("BCIC_EXAMPLE_OBJECT", "Contact")
    record_id = os.environ.get("BCIC_EXAMPLE_RECORD_ID", "RECORD_ID")
    with Client.from_env() as client:
        record = client.records.get(object_name, record_id)
        print(record.record_id, sorted(record.fields))


if __name__ == "__main__":
    main()
