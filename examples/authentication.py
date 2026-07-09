"""Authenticate explicitly and close the BCIC session safely."""

from bcic import Client


def main() -> None:
    """Authenticate using environment configuration and terminate the session."""
    with Client.from_env() as client:
        client.authenticate()
        print("Authenticated successfully")
        client.logout()


if __name__ == "__main__":
    main()
