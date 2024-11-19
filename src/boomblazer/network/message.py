"""Define all messages types"""

import enum


class Message(enum.IntEnum):
    """Represent a message type"""

    NULL = 0
    NAME = enum.auto()
    SPAWN = enum.auto()
    DESPAWN = enum.auto()
    OK = enum.auto()
    NOK = enum.auto()
    LOBBY_INFO = enum.auto()
    ID = enum.auto()
    READY = enum.auto()
    NOT_READY = enum.auto()
    MAP = enum.auto()
    DISCONNECT = enum.auto()
    START = enum.auto()
    PLAYER_ACTIONS = enum.auto()
