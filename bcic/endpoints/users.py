"""Typed user, role, and permission operations."""

from collections.abc import Mapping

from bcic.endpoints.base import BaseEndpoint
from bcic.exceptions import ValidationError
from bcic.models.records import JSONValue, validate_identifier
from bcic.models.users import (
    Permission,
    PermissionEntityType,
    Role,
    normalize_permissions,
    normalize_role,
    normalize_roles,
)


class UsersEndpoint(BaseEndpoint):
    """Entry point for typed role and permission operations."""

    REST_METHODS = (
        "getRoles",
        "getRoleById",
        "getPermissionsByRole",
        "getPermissionsByUser",
    )

    def _execute(
        self, method_name: str, parameters: Mapping[str, JSONValue] | None = None
    ) -> dict[str, JSONValue] | list[JSONValue]:
        payload = dict(parameters or {})
        payload["output"] = self._context.config.output_format
        return self._context.transport.transport.execute(
            method_name,
            payload,
            output_format=self._context.config.output_format,
        )

    def list_roles(self) -> list[Role]:
        """Return all visible roles; BCIC omits Super Admin.

        Raises:
            ValidationError: If the complete response cannot be normalized.
            BCICError: For mapped request failures.
        """
        return normalize_roles(self._execute("getRoles"))

    def get_role(self, role_id: str) -> Role:
        """Return a role by its BCIC original ID, not its tenant-local ID.

        Args:
            role_id: Non-empty BCIC original role identifier.

        Raises:
            ValidationError: If input or response data is invalid.
            BCICError: For mapped request failures.
        """
        payload = self._execute(
            "getRoleById", {"roleId": validate_identifier(role_id, "role ID")}
        )
        return normalize_role(payload)

    def get_permissions_by_role(
        self,
        role_id: str,
        entity_type: PermissionEntityType | str,
        *,
        object_id: str | None = None,
        application_id: str | None = None,
    ) -> list[Permission]:
        """Return permissions assigned through a role original ID.

        Args:
            role_id: BCIC original role identifier.
            entity_type: Supported permission entity type.
            object_id: Required only for object-dependent entity types.
            application_id: Required only for menu permissions.

        Raises:
            ValidationError: If identifiers, dependencies, or data are invalid.
            BCICError: For mapped request failures.
        """
        return self._get_permissions(
            "getPermissionsByRole",
            "roleId",
            role_id,
            entity_type,
            object_id,
            application_id,
            allow_field=True,
        )

    def get_permissions_by_user(
        self,
        user_id: str,
        entity_type: PermissionEntityType | str,
        *,
        object_id: str | None = None,
        application_id: str | None = None,
    ) -> list[Permission]:
        """Return permissions assigned to one documented BCIC user ID.

        Args:
            user_id: Documented BCIC user identifier.
            entity_type: Supported non-field permission entity type.
            object_id: Required only for object-dependent entity types.
            application_id: Required only for menu permissions.

        Raises:
            ValidationError: If identifiers, dependencies, or data are invalid.
            BCICError: For mapped request failures.
        """
        return self._get_permissions(
            "getPermissionsByUser",
            "userId",
            user_id,
            entity_type,
            object_id,
            application_id,
            allow_field=False,
        )

    def _get_permissions(
        self,
        method_name: str,
        subject_key: str,
        subject_id: str,
        entity_type: PermissionEntityType | str,
        object_id: str | None,
        application_id: str | None,
        *,
        allow_field: bool,
    ) -> list[Permission]:
        subject = validate_identifier(subject_id, "subject ID")
        try:
            entity = PermissionEntityType(entity_type)
        except (ValueError, TypeError) as error:
            raise ValidationError("Invalid permission entity type") from error
        if entity is PermissionEntityType.FIELD and not allow_field:
            raise ValidationError("Invalid permission entity type")
        needs_object = entity in {
            PermissionEntityType.FIELD,
            PermissionEntityType.VIEW,
            PermissionEntityType.ACTION,
            PermissionEntityType.REPORT,
            PermissionEntityType.CHART,
        }
        needs_application = entity is PermissionEntityType.MENU
        if needs_object != (object_id is not None):
            raise ValidationError("Invalid object ID dependency")
        if needs_application != (application_id is not None):
            raise ValidationError("Invalid application ID dependency")
        parameters: dict[str, JSONValue] = {
            subject_key: subject,
            "entityType": entity.value,
        }
        if object_id is not None:
            parameters["objId"] = validate_identifier(object_id, "object ID")
        if application_id is not None:
            parameters["appId"] = validate_identifier(application_id, "application ID")
        return normalize_permissions(
            self._execute(method_name, parameters),
            allow_conditional=allow_field and entity is PermissionEntityType.FIELD,
        )
