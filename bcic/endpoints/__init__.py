"""Domain endpoint types composed by :class:`bcic.Client`."""

from bcic.endpoints.binary import BinaryEndpoint
from bcic.endpoints.methods import MethodsEndpoint
from bcic.endpoints.records import RecordsEndpoint
from bcic.endpoints.users import UsersEndpoint

__all__ = ["BinaryEndpoint", "MethodsEndpoint", "RecordsEndpoint", "UsersEndpoint"]
