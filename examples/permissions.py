"""Read role and permission data through the high-level user endpoint."""

import os

from bcic import Client
from bcic.models import PermissionEntityType


def main() -> None:
    """List roles and optionally inspect one role's object permissions."""
    with Client.from_env() as client:
        roles = client.users.list_roles()
        print([role.name for role in roles])
        role_id = os.environ.get("BCIC_EXAMPLE_ROLE_ID")
        if role_id:
            permissions = client.users.get_permissions_by_role(
                role_id, PermissionEntityType.OBJECT
            )
            print([permission.name for permission in permissions])


if __name__ == "__main__":
    main()
