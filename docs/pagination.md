# Pagination

`client.records.get_page()` returns `Page[DynamicRecord]`, containing `items`
and `PageMetadata`. `start_row` is zero-based and `page_size` defaults to 100.

```python
from bcic import Client
from bcic.pagination import EqualityFilter

with Client.from_env() as client:
    page = client.records.get_page(
        "VIEW_ID",
        page_size=50,
        equality_filter=EqualityFilter(name="Status", value="Active"),
    )
    for record in page.items:
        print(record.record_id)
```

`list_all()` traverses eagerly without replaying successful pages. Always set
limits suitable for your workload:

```python
from bcic import Client

with Client.from_env() as client:
    records = client.records.list_all(
        "VIEW_ID",
        page_size=100,
        max_pages=20,
        max_items=2_000,
    )
```

The helper stops on an empty/short page or authoritative completion metadata.
It raises `PaginationLimitError` rather than returning silently truncated
results, and raises `ValidationError` if pagination does not advance.
