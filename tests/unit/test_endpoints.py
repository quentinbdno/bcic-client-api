from bcic import Client
from bcic.endpoints import (
    BinaryEndpoint,
    MethodsEndpoint,
    RecordsEndpoint,
    UsersEndpoint,
)


def configured_client() -> Client:
    return Client(
        base_url="https://example.bcic.test",
        username="integration-user",
        password="secret-value",
    )


def test_client_exposes_cached_domain_endpoints() -> None:
    client = configured_client()

    assert isinstance(client.records, RecordsEndpoint)
    assert isinstance(client.users, UsersEndpoint)
    assert isinstance(client.binary, BinaryEndpoint)
    assert isinstance(client.methods, MethodsEndpoint)
    assert client.records is client.records
    assert client.users is client.users
    assert client.binary is client.binary
    assert client.methods is client.methods


def test_endpoints_share_one_private_composition_context() -> None:
    client = configured_client()
    endpoints = (client.records, client.users, client.binary, client.methods)

    contexts = {id(endpoint._context) for endpoint in endpoints}
    assert len(contexts) == 1
    assert client.records._context.config is client.config
    assert client.records._context.authentication.config is client.config
    assert client.records._context.transport.config is client.config
    assert client.records._context.parser.config is client.config
    assert not hasattr(client.records, "base_url")
    assert not hasattr(client.records, "session_id")
    assert not hasattr(client.records, "http_client")


def test_rest_method_metadata_is_owned_by_each_endpoint_module() -> None:
    endpoints = (RecordsEndpoint, UsersEndpoint, BinaryEndpoint, MethodsEndpoint)

    assert all(endpoint.REST_METHODS == () for endpoint in endpoints)
