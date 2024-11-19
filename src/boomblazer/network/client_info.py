"""Define the information given by a client"""

from ..environment.position import NULL_POSITION
from ..environment.position import Position


class ClientInfo:
    """Client info"""

    __slots__ = {
        "id": "(int) Client's ID number",
        "name": "(str) Client's name",
        "spawn_point": "(Position) Player's spawn position at game start",
        "is_ready": "(bool) Tells if the players is ready to play",
        "skin": "(int) Player's skin for in game display",
    }

    def __init__(
        self,
        id_: int,
        name: bytes = b"",
        spawn_point: Position = NULL_POSITION,
        is_ready: bool = False,
        skin: int = 0,
    ) -> None:
        """Initialize client info

        :param id_: Defines the client's id number
        :param name: Defines the client's name
        :param spawn_point: Defines where the player will spawn at game start
        :param is_ready: Tells if the player is ready to play
        :param skin: The player's skin for in game display
        """
        self.id = id_
        self.name = name
        self.spawn_point = spawn_point
        self.is_ready = is_ready
        self.skin = skin

    def __repr__(self) -> str:
        """Client info textual representation for logging"""
        return (
            f"{self.__class__.__name__}("
            f"{self.id!r}, {self.name!r}, {self.spawn_point!r}, {self.is_ready!r}, "
            f"{self.skin!r}"
            ")"
        )
