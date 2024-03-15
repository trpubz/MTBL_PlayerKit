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
    player_stats: Dict[str, Any] = {}
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
        player_stats = add_player_stats_data(data[3:], positions, espn_id)

        return cls(name=name,
                   ovr=ovr,
                   positions=positions,
                   team=team,
                   owner=owner,
                   player_stats=player_stats,
                   espn_id=espn_id)


def add_player_stats_data(data: list, positions: list, player_id: str) -> dict[str: float]:
    """
    Adds player rater data to the player object.
    :param player_id: need to check for shohei or any 2 way players
    :param data: list of HTML <td> tags data from ESPN
    :param positions: [string] of player positions
    :return: dictionary of player rater data
    """
    player_stats = {}
    for d in data:
        try:
            cat = d.find("div")["title"]
        except KeyError:  # indicates no title attribute is found
            continue
        if ("SP" not in positions and "RP" not in positions) or player_id == "39832":
            match cat:
                case "Runs Scored":
                    player_stats.update({"R": safe_float(d.get_text(strip=True))})
                case "Home Runs":
                    player_stats.update({"HR": safe_float(d.get_text(strip=True))})
                case "Runs Batted In":
                    player_stats.update({"RBI": safe_float(d.get_text(strip=True))})
                case "Net Stolen Bases":
                    player_stats.update({"SBN": safe_float(d.get_text(strip=True))})
                case "On Base Pct":
                    player_stats.update({"OBP": safe_float(d.get_text(strip=True))})
                case "Slugging Pct":
                    player_stats.update({"SLG": safe_float(d.get_text(strip=True))})

            continue
        if "SP" in positions or "RP" in positions:
            match cat:
                case "Innings Pitched":
                    player_stats.update({"IP": safe_float(d.get_text(strip=True))})
                case "Quality Starts":
                    player_stats.update({"QS": safe_float(d.get_text(strip=True))})
                case "Earned Run Average":
                    player_stats.update({"ERA": safe_float(d.get_text(strip=True))})
                case "Walks plus Hits Per Innings Pitched":
                    player_stats.update({"WHIP": safe_float(d.get_text(strip=True))})
                case "Strikeouts per 9 Innings":
                    player_stats.update({"K/9": safe_float(d.get_text(strip=True))})
                case "Saves Plus Holds":
                    player_stats.update({"SVHD": safe_float(d.get_text(strip=True))})

            continue
        match cat:
            case _ if re.match(".*rostered.*", cat):
                player_stats.update({"%ROST": safe_float(d.get_text(strip=True))})
            case _ if re.match(".*Rating.*", cat):
                player_stats.update({"PRTR": safe_float(d.get_text(strip=True))})

    return player_stats


def safe_float(text_value):
    if text_value == "--":
        return None
    else:
        return float(text_value)