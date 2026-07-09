"""Encapsulated REST v1 session authentication."""

import logging

from bcic.config import ClientConfig
from bcic.exceptions import AuthenticationError
from bcic.transport import RestTransport

logger = logging.getLogger(__name__)


class SessionAuth:
    """Authenticate lazily and keep the BCIC session identifier private."""

    def __init__(self, config: ClientConfig, transport: RestTransport) -> None:
        self._config = config
        self._transport = transport
        self._session_id: str | None = None

    def authenticate(self) -> None:
        """Establish a session explicitly, reusing an active session."""
        if self._session_id is not None:
            logger.debug("Authentication session reused")
            return
        logger.info("Authentication started")
        payload = self._transport.execute(
            "login",
            {"output": "json"},
            http_method="POST",
            headers={
                "loginName": self._config.username,
                "password": self._config.password.get_secret_value(),
            },
            authenticate=False,
        )
        if not isinstance(payload, dict):
            logger.warning("Authentication failed")
            raise AuthenticationError("BCIC authentication failed")
        session_id = payload.get("sessionId")
        if payload.get("status") != "ok" or not isinstance(session_id, str):
            logger.warning("Authentication failed")
            raise AuthenticationError("BCIC authentication failed")
        normalized_session_id = session_id.strip()
        if not normalized_session_id:
            logger.warning("Authentication failed")
            raise AuthenticationError("BCIC authentication failed")
        self._session_id = normalized_session_id
        logger.info("Authentication succeeded")

    def request_headers(self) -> dict[str, str]:
        """Return headers for an authenticated request."""
        self.authenticate()
        if self._session_id is None:  # pragma: no cover - authenticate guarantees it
            raise AuthenticationError("BCIC authentication failed")
        return {"sessionId": self._session_id}

    def logout(self) -> None:
        """Terminate an active session and always clear local state."""
        session_id = self._session_id
        if session_id is None:
            logger.debug("Logout skipped; no active session")
            return
        logger.info("Logout started")
        try:
            self._transport.execute(
                "logout",
                http_method="GET",
                headers={"sessionId": session_id},
                authenticate=False,
            )
        finally:
            self._session_id = None
            logger.info("Logout completed")
