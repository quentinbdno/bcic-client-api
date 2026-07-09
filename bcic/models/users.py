"""Typed models and normalization for BCIC users and permissions."""

from collections.abc import Mapping
from enum import StrEnum
from typing import Literal, cast, overload

from pydantic import Field

from bcic.exceptions import ValidationError
from bcic.models.common import SDKModel


class Role(SDKModel):
    """One BCIC authorization role."""

    name: str = Field(min_length=1)
    integration_code: str | None = None
    description: str | None = None
    id: str = Field(min_length=1)
    original_id: str = Field(min_length=1)


class PermissionEntityType(StrEnum):
    """Entity types accepted by BCIC permission methods."""

    FIELD = "field"
    OBJECT = "object"
    APPLICATION = "application"
    MENU = "menu"
    VIEW = "view"
    ACTION = "action"
    REPORT = "report"
    CHART = "chart"


type PermissionValue = bool | Literal["conditional"]


class Permission(SDKModel):
    """Entity identity and its dynamic permission-name values."""

    name: str = Field(min_length=1)
    id: str = Field(min_length=1)
    original_id: str = Field(min_length=1)
    permissions: dict[str, PermissionValue]


@overload
def _text(value: object, *, optional: Literal[False] = False) -> str: ...


@overload
def _text(value: object, *, optional: Literal[True]) -> str | None: ...


def _text(value: object, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str):
        raise ValidationError("Invalid user-domain response")
    normalized = value.strip()
    if not normalized and not optional:
        raise ValidationError("Invalid user-domain response")
    return normalized


def normalize_role(payload: object) -> Role:
    """Normalize one role without leaking malformed response values."""
    if not isinstance(payload, Mapping):
        raise ValidationError("Invalid role response")
    try:
        return Role(
            name=_text(payload.get("name")),
            integration_code=_text(payload.get("integrationCode"), optional=True),
            description=_text(payload.get("description"), optional=True),
            id=_text(payload.get("id")),
            original_id=_text(payload.get("originalId")),
        )
    except ValidationError as error:
        raise ValidationError("Invalid role response") from error


def normalize_roles(payload: object) -> list[Role]:
    """Atomically normalize a top-level role array."""
    if not isinstance(payload, list):
        raise ValidationError("Invalid roles response")
    try:
        return [normalize_role(item) for item in payload]
    except ValidationError as error:
        raise ValidationError("Invalid roles response") from error


def normalize_permissions(payload: object) -> list[Permission]:
    """Atomically normalize a top-level permission array."""
    if not isinstance(payload, list):
        raise ValidationError("Invalid permissions response")
    results: list[Permission] = []
    try:
        for item in payload:
            if not isinstance(item, Mapping):
                raise ValidationError("Invalid permission response")
            permissions: dict[str, PermissionValue] = {}
            for key, value in item.items():
                if key in {"name", "id", "originalId"}:
                    continue
                if not isinstance(key, str) or not key.strip():
                    raise ValidationError("Invalid permission response")
                if isinstance(value, bool) or value == "conditional":
                    permissions[key] = cast(PermissionValue, value)
                else:
                    raise ValidationError("Invalid permission response")
            results.append(
                Permission(
                    name=_text(item.get("name")),
                    id=_text(item.get("id")),
                    original_id=_text(item.get("originalId")),
                    permissions=permissions,
                )
            )
    except ValidationError as error:
        raise ValidationError("Invalid permissions response") from error
    return results
