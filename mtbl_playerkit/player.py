"""
This module contains the Player class which inherits pydantic BaseModel for serialization.
"""
from typing import Any
from pydantic import BaseModel


class Player(BaseModel):
    def __init__(self, name, team, /, *args, **data: Any):
        super().__init__(**data)
        self._name = name
        self.team = team
