import ast
import inspect
from types import ModuleType

import httpx

import bcic.endpoints.binary
import bcic.endpoints.methods
import bcic.endpoints.records
import bcic.endpoints.users
from bcic import Client
from bcic._wiring import RestV1Adapter, RestV2Adapter, resolve_adapter_set
from tests.unit.fakes import RequestRecorder, json_response


def test_default_client_resolves_v1_adapter_set() -> None:
    client = Client(
        base_url="https://example.bcic.test",
        username="integration-user",
        password="secret-value",
    )

    assert isinstance(client._transport._adapter, RestV1Adapter)


def test_v2_client_resolves_distinct_adapter_set() -> None:
    client = Client(
        base_url="https://example.bcic.test",
        username="integration-user",
        password="secret-value",
        api_version="v2",
    )

    assert isinstance(client._transport._adapter, RestV2Adapter)
    assert type(client._transport._adapter) is not type(
        resolve_adapter_set("v1").transport
    )


def test_version_adapters_preserve_current_request_paths() -> None:
    recorder = RequestRecorder(lambda _: json_response({"status": "ok"}))
    http_client = httpx.Client(transport=httpx.MockTransport(recorder))

    v1 = resolve_adapter_set("v1").create_transport(
        "https://example.test/root",
        client=http_client,
        max_retries=0,
    )
    v1.execute("getRecord", {"id": "42"})

    v2 = resolve_adapter_set("v2").create_transport(
        "https://example.test/root",
        client=http_client,
        max_retries=0,
    )
    v2.execute("doThing", {"value": 1}, http_method="POST")

    assert recorder.requests[0].url == (
        "https://example.test/root/rest/api/getRecord?id=42"
    )
    assert recorder.requests[1].url == "https://example.test/root/customMethod/doThing"
    assert recorder.requests[1].headers["Accept-Version"] == "latest"


def test_endpoint_modules_do_not_branch_on_api_version() -> None:
    endpoint_modules = (
        bcic.endpoints.binary,
        bcic.endpoints.methods,
        bcic.endpoints.records,
        bcic.endpoints.users,
    )

    for module in endpoint_modules:
        assert _version_branch_conditions(module) == []


def _version_branch_conditions(module: ModuleType) -> list[int]:
    tree = ast.parse(inspect.getsource(module))
    branch_lines: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and _mentions_version(node.test):
            branch_lines.append(node.lineno)
    return branch_lines


def _mentions_version(node: ast.AST) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Name) and child.id in {"api_version", "version"}:
            return True
        if isinstance(child, ast.Attribute) and child.attr in {
            "api_version",
            "version",
        }:
            return True
        if isinstance(child, ast.Constant) and child.value in {"v1", "v2"}:
            return True
    return False
