"""
Player Factory that creates various types of players.
"""
import bs4 as bs

from mtbl_playerkit.espn_player import ESPNPlayer


class PlayerFactory:
    """
    Factory class to create various types of players.
    """
    @staticmethod
    def create_players(source: str, *args, **kwargs):
        """
        Create a list of players from a given source.
        :param source: should be one of "ESPN", "FANGRAPHS", "SAVANT"
        :param args: typically a read HTML file
        :param kwargs: pro re nata
        :return: list of Player objects
        """
        match source:
            case "ESPN":
                raw_players = bs.BeautifulSoup(args[0], "lxml").find_all("tr")
                return [ESPNPlayer.from_data(player.find_all("td")) for player in raw_players]
            case _:
                raise ValueError(f"Unknown data source: {source}")
