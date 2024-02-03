"""
This module contains the Player class which inherits pydantic BaseModel for serialization.
"""
from pydantic import BaseModel


class Player(BaseModel):
    """
    This class represents a player. Conforms to the pydantic BaseModel for serialization.
    attributes are declared as fields.
    """
    name: str
    team: str
