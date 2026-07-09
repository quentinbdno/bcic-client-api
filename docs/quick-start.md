# Quick Start

Constructing a client validates configuration but does not contact BCIC.
Authentication is lazy: the first endpoint request logs in and retains the
session internally.

```python
from bcic import Client
from bcic.exceptions import BCICError, NotFoundError

try:
    with Client(
        base_url="https://example.bcic.test",
        username="YOUR_USERNAME",
        password="YOUR_PASSWORD",
    ) as client:
        record = client.records.get("Contact", "RECORD_ID")
        print(record.record_id, record.fields)
except NotFoundError:
    print("The record does not exist")
except BCICError as error:
    print(f"BCIC operation failed: {error}")
```

`Client.from_env()` is preferred when configuration comes from the process
environment. See [authentication](authentication.md) and [errors](errors.md).
Use domain endpoints for normal application code. Reserve
`client.methods.execute()` for documented methods with no high-level wrapper.
