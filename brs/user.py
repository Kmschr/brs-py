"""User and brick owner classes for Brickadia save files.

This module provides classes for representing users and brick owners
in Brickadia save files.
"""
from typing import Optional
from uuid import UUID


class User:
    """Represents a user in a Brickadia save file.
    
    Attributes:
        name: User's display name.
        uuid: User's unique identifier.
    """
    
    def __init__(self, name: str, uuid: UUID) -> None:
        """Initialize a User.
        
        Args:
            name: User's display name.
            uuid: User's unique identifier.
        """
        self.name = name
        self.uuid = uuid

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return '{} ({})'.format(self.name, self.uuid)


class BrickOwner(User):
    """Represents a brick owner with brick count.
    
    Attributes:
        name: Owner's display name.
        uuid: Owner's unique identifier.
        brickcount: Number of bricks owned.
    """
    
    def __init__(self, name: str, uuid: UUID, brickcount: int) -> None:
        """Initialize a BrickOwner.
        
        Args:
            name: Owner's display name.
            uuid: Owner's unique identifier.
            brickcount: Number of bricks owned.
            
        Raises:
            ValueError: If brickcount is negative.
        """
        if brickcount < 0:
            raise ValueError(f"Brick count must be non-negative, got {brickcount}")
        super().__init__(name, uuid)
        self.brickcount = brickcount

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return '{} {:,} bricks'.format(super().__str__(), self.brickcount)