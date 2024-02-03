
from mtbl_playerkit.espn_player import ESPNPlayer


class PlayerFactory:
    @staticmethod
    def create_player(source: str, *args, **kwargs):
        match source:
            case "ESPN":
                return ESPNPlayer.from_data(*args, **kwargs)
            case _:
                raise ValueError(f"Unknown data source: {source}")
