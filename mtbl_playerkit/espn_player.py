"""
This module contains the ESPNPlayer class which is a subclass of Player.
"""
import re
from typing import Any, Dict, List

from mtbl_playerkit import Player


class ESPNPlayer(Player):
    """
    This class represents a player from ESPN.
    """
    owner: str
    ovr: int
    positions: List[str] = []
    player_rater: Dict[str, Any] = {}
    espn_id: str

    @classmethod
    def from_data(cls, data: list):
        """
        Creates an ESPNPlayer object from a list of HTML data.
        :param data: HTML data from ESPN
        :return: None
        """
        id_loc: str = (data[1].find("img").get("data-src")
                       or
                       data[1].find("img").get("src"))
        try:
            espn_id = re.findall(r'full/(\d+)\.png', id_loc)[0]
        except IndexError as ie:
            print(
                f"Error processing html for {data[1].get_text(strip=True)}."
                f"Error message: {ie}")
            raise IndexError("Could not find ESPN ID")
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
    :param data: list of HTML <td> tags data from ESPN
    :param positions: [string] of player positions
    :return: dictionary of player rater data
    """
    player_rater = {}
    for d in data:
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
