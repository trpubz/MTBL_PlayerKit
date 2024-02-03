"""
This module contains the ESPNPlayer class which is a subclass of Player.
"""
import re

from mtbl_playerkit import Player


class ESPNPlayer(Player):
    def __init__(self, *args, name, team, ovr, owner, player_rater, espn_id, **kwargs):
        super().__init__(name, team, *args, **kwargs)
        self.ovr = ovr
        self.owner = owner
        self.player_rater = player_rater or {}
        self.espn_id = espn_id

    @classmethod
    def from_data(cls, data: list, espn_id: str):
        """
        Creates an ESPNPlayer object from a list of HTML data.
        :param data: HTML data from ESPN
        :param espn_id: string representing the ESPN ID of the player
        :return: None
        """
        name = data[1].find("a", class_="AnchorLink").get_text(strip=True)
        ovr = int(data[0].text)
        regex_pos = re.compile(".*playerpos.*")
        positions: list = data[1].find("span", class_=regex_pos).get_text(strip=True).split(", ")
        # sometimes position players can have RP stats when their team gets blown up, so this
        # removes RP from the position player
        if len(positions) > 1 and "RP" in positions and "SP" not in positions:
            positions.remove("RP")
        regex_tm = re.compile(".*playerteam.*")
        team = data[1].find(class_=regex_tm).get_text(strip=True).upper()
        # if the owner is not listed, then the player is a free agent and the splitting the text
        # will drop the waiver date and return only WA
        owner = data[2].get_text(strip=True).split(" ")[0]
        player_rater = add_player_rater_data(data[3:], positions)

        return cls(name=name,
                   ovr=ovr,
                   positions=positions,
                   team=team,
                   owner=owner,
                   player_rater=player_rater,
                   espn_id=espn_id)


def add_player_rater_data(data: list, positions: list) -> dict[str: float]:
    """
    Adds player rater data to the player object.
    :param data: list of HTML data from ESPN
    :param positions:
    :return: dictionary of player rater data
    """
    player_rater = {}
    for d in data:
        cat = ""
        try:
            cat = d.find("div")["title"]
        except KeyError:  # indicates no title attribute is found
            continue
        if any(p for p in positions if "SP" not in p or "RP" not in p):
            match cat:
                case "Runs Scored":
                    player_rater.update({"R": float(d.get_text(strip=True))})
                    continue
                case "Home Runs":
                    player_rater.update({"HR": float(d.get_text(strip=True))})
                    continue
                case "Runs Batted In":
                    player_rater.update({"RBI": float(d.get_text(strip=True))})
                    continue
                case "Net Stolen Bases":
                    player_rater.update({"SBN": float(d.get_text(strip=True))})
                    continue
                case "On Base Pct":
                    player_rater.update({"OBP": float(d.get_text(strip=True))})
                    continue
                case "Slugging Pct":
                    player_rater.update({"SLG": float(d.get_text(strip=True))})
                    continue
        if any(p for p in positions if "SP" in p or "RP" in p):
            match cat:
                case "Innings Pitched":
                    player_rater.update({"IP": float(d.get_text(strip=True))})
                    continue
                case "Quality Starts":
                    player_rater.update({"QS": float(d.get_text(strip=True))})
                    continue
                case "Earned Run Average":
                    player_rater.update({"ERA": float(d.get_text(strip=True))})
                    continue
                case "Walks plus Hits Per Innings Pitched":
                    player_rater.update({"WHIP": float(d.get_text(strip=True))})
                    continue
                case "Strikeouts per 9 Innings":
                    player_rater.update({"K/9": float(d.get_text(strip=True))})
                    continue
                case "Saves Plus Holds":
                    player_rater.update({"SVHD": float(d.get_text(strip=True))})
                    continue
        match cat:
            case _ if re.match(".*rostered.*", cat):
                player_rater.update({"%ROST": float(d.get_text(strip=True))})
            case _ if re.match(".*Rating.*", cat):
                try:
                    player_rater.update({"PRTR": float(d.get_text(strip=True))})
                except ValueError:  # will raise if the player rater is "--"
                    player_rater.update({"PRTR": 0.0})

    return player_rater
