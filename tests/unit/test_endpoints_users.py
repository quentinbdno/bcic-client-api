import httpx
import pytest

from bcic import Client
from bcic.exceptions import AuthorizationError, NotFoundError, ValidationError
from bcic.models import PermissionEntityType


def make_client(
    requests: list[httpx.Request], payload: object, *, status_code: int = 200
) -> Client:
    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/login"):
            return httpx.Response(200, json={"status": "ok", "sessionId": "sid"})
        return httpx.Response(status_code, json=payload)

    return Client(
        base_url="https://example.test",
        username="user",
        password="password",
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )


def test_list_roles_normalizes_array_and_request() -> None:
    requests: list[httpx.Request] = []
    client = make_client(
        requests,
        [
            {
                "name": "Admin",
                "integrationCode": None,
                "description": "",
                "id": "7",
                "originalId": "role-7",
            }
        ],
    )

    roles = client.users.list_roles()

    assert roles[0].original_id == "role-7"
    assert roles[0].description == ""
    assert dict(requests[1].url.params) == {"output": "json"}


def test_get_role_uses_original_id() -> None:
    requests: list[httpx.Request] = []
    client = make_client(
        requests,
        {"name": "Admin", "id": "7", "originalId": "role-7"},
    )

    assert client.users.get_role(" role-7 ").name == "Admin"
    assert dict(requests[1].url.params) == {
        "roleId": "role-7",
        "output": "json",
    }


@pytest.mark.parametrize("role_id", ["", " "])
def test_get_role_rejects_invalid_id_without_request(role_id: str) -> None:
    requests: list[httpx.Request] = []
    client = make_client(requests, {})
    with pytest.raises(ValidationError):
        client.users.get_role(role_id)
    assert requests == []


@pytest.mark.parametrize("payload", [{}, [None], [{"name": "x", "id": "1"}]])
def test_roles_reject_malformed_data_atomically(payload: object) -> None:
    client = make_client([], payload)
    with pytest.raises(ValidationError):
        client.users.list_roles()


@pytest.mark.parametrize(
    ("status", "exception"),
    [(403, AuthorizationError), (404, NotFoundError)],
)
def test_role_failures_remain_mapped(status: int, exception: type[Exception]) -> None:
    with pytest.raises(exception):
        make_client([], {}, status_code=status).users.get_role("role")


@pytest.mark.parametrize(
    ("entity", "object_id", "application_id", "expected"),
    [
        ("object", None, None, {}),
        ("field", "object-1", None, {"objId": "object-1"}),
        ("view", "object-1", None, {"objId": "object-1"}),
        ("menu", None, "app-1", {"appId": "app-1"}),
    ],
)
def test_role_permission_dependency_matrix(
    entity: str,
    object_id: str | None,
    application_id: str | None,
    expected: dict[str, str],
) -> None:
    requests: list[httpx.Request] = []
    client = make_client(
        requests,
        [
            {
                "name": "Contact",
                "id": "3",
                "originalId": "contact",
                "read": True,
                "write": False,
            }
        ],
    )
    result = client.users.get_permissions_by_role(
        "role", entity, object_id=object_id, application_id=application_id
    )
    assert result[0].permissions["read"] is True
    assert result[0].permissions["write"] is False
    params = dict(requests[1].url.params)
    assert params == {
        "roleId": "role",
        "entityType": entity,
        **expected,
        "output": "json",
    }


def test_user_permissions_reject_field_without_request() -> None:
    requests: list[httpx.Request] = []
    client = make_client(requests, [])
    with pytest.raises(ValidationError):
        client.users.get_permissions_by_user(
            "user", PermissionEntityType.FIELD, object_id="object"
        )
    assert requests == []


def test_role_field_permissions_allow_conditional_value() -> None:
    result = make_client(
        [],
        [
            {
                "name": "Contact",
                "id": "3",
                "originalId": "contact",
                "special": "conditional",
            }
        ],
    ).users.get_permissions_by_role("role", "field", object_id="object-1")

    assert result[0].permissions["special"] == "conditional"


@pytest.mark.parametrize(
    ("subject", "entity", "object_id", "application_id"),
    [
        ("role", "object", None, None),
        ("role", "view", "object-1", None),
        ("role", "menu", None, "app-1"),
        ("user", "object", None, None),
        ("user", "view", "object-1", None),
        ("user", "menu", None, "app-1"),
    ],
)
def test_non_role_field_permissions_reject_conditional_value(
    subject: str, entity: str, object_id: str | None, application_id: str | None
) -> None:
    client = make_client(
        [],
        [
            {
                "name": "Contact",
                "id": "3",
                "originalId": "contact",
                "special": "conditional",
            }
        ],
    )

    with pytest.raises(ValidationError):
        if subject == "role":
            client.users.get_permissions_by_role(
                "role", entity, object_id=object_id, application_id=application_id
            )
        else:
            client.users.get_permissions_by_user(
                "user", entity, object_id=object_id, application_id=application_id
            )


@pytest.mark.parametrize(
    ("entity", "object_id", "application_id"),
    [
        ("view", None, None),
        ("object", "extra", None),
        ("menu", None, None),
        ("menu", None, " "),
        ("application", None, "extra"),
        ("unknown", None, None),
    ],
)
def test_permissions_reject_invalid_dependencies_without_request(
    entity: str, object_id: str | None, application_id: str | None
) -> None:
    requests: list[httpx.Request] = []
    client = make_client(requests, [])
    with pytest.raises(ValidationError):
        client.users.get_permissions_by_role(
            "role", entity, object_id=object_id, application_id=application_id
        )
    assert requests == []


@pytest.mark.parametrize(
    "payload",
    [
        {},
        [None],
        [{"name": "x", "id": "1", "originalId": "x", "read": "yes"}],
        [
            {"name": "x", "id": "1", "originalId": "x", "read": True},
            {"name": "bad"},
        ],
    ],
)
def test_permissions_reject_malformed_collection(payload: object) -> None:
    with pytest.raises(ValidationError):
        make_client([], payload).users.get_permissions_by_role("role", "object")
