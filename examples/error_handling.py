"""Handle typed SDK failures without depending on raw HTTP exceptions."""

from bcic import Client
from bcic.exceptions import AuthorizationError, BCICError, NotFoundError


def main() -> None:
    """Demonstrate specific and common SDK exception handling."""
    try:
        with Client.from_env() as client:
            client.records.get("Contact", "RECORD_ID")
    except NotFoundError:
        print("Record not found")
    except AuthorizationError:
        print("Permission denied")
    except BCICError as error:
        print(f"BCIC request failed: {error}")


if __name__ == "__main__":
    main()
