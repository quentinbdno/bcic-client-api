"""Traverse records with explicit page and item safeguards."""

import os

from bcic import Client


def main() -> None:
    """List a bounded number of records from an environment-selected view."""
    view_id = os.environ.get("BCIC_EXAMPLE_VIEW_ID", "VIEW_ID")
    with Client.from_env() as client:
        records = client.records.list_all(
            view_id,
            page_size=100,
            max_pages=10,
            max_items=1_000,
        )
        print(f"Retrieved {len(records)} records")


if __name__ == "__main__":
    main()
