"""
This module contains the ESPNPlayer class which is a subclass of Player.
"""
import numbers
import re
from typing import Any, Dict, List

from mtbl_playerkit import Player
from mtbl_playerkit.src.mtbl_globals import ETLType


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
    def from_data(cls, data: list, etl_type: ETLType):
        """
        Creates an ESPNPlayer object from a list of HTML data.
        :param data: HTML data from ESPN
        :param etl_type: PRESZN or REGSZN
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
        player_stats = add_player_stats_data(data[3:], positions, espn_id, etl_type)

        return cls(name=name,
                   ovr=ovr,
                   positions=positions,
                   team=team,
                   owner=owner,
                   player_stats=player_stats,
                   espn_id=espn_id)


def add_player_stats_data(data: list, positions: list, player_id: str, etl_type: ETLType) \
        -> dict[str: Any]:
    """
    Adds player rater data to the player object.
    :param player_id: need to check for shohei or any 2 way players
    :param data: list of HTML <td> tags data from ESPN
    :param etl_type: PRE or REG SZN
    :param positions: [string] of player positions
    :return: dictionary of player rater data
    """
    player_stats = {}
    for d in data:
        try:
            cat = d.find("div")["title"]

        except KeyError:  # indicates no title attribute is found
            continue
        value = d.get_text(strip=True)
        key = ""
        if ("SP" not in positions and "RP" not in positions) or player_id == "39832":
            match cat:
                case "Runs Scored":
                    player_stats.update({"R":
                                         safe_int(value) if etl_type == ETLType.PRE_SZN else
                                         safe_float(value)})
                case "Home Runs":
                    player_stats.update({"HR":
                                         safe_int(value) if etl_type == ETLType.PRE_SZN else
                                         safe_float(value)})
                case "Runs Batted In":
                    player_stats.update({"RBI":
                                         safe_int(value) if etl_type == ETLType.PRE_SZN else
                                         safe_float(value)})
                case "Net Stolen Bases":
                    player_stats.update({"SBN":
                                         safe_int(value) if etl_type == ETLType.PRE_SZN else
                                         safe_float(value)})
                case "On Base Pct":
                    player_stats.update({"OBP": safe_float(value)})
                case "Slugging Pct":
                    player_stats.update({"SLG": safe_float(value)})

        if "SP" in positions or "RP" in positions:
            match cat:
                case "Innings Pitched":
                    player_stats.update({"IP": safe_float(value)})
                case "Quality Starts":
                    player_stats.update({"QS":safe_int(value) if etl_type == ETLType.PRE_SZN else
                                         safe_float(value)})
                case "Earned Run Average":
                    player_stats.update({"ERA": safe_float(value)})
                case "Walks plus Hits Per Innings Pitched":
                    player_stats.update({"WHIP": safe_float(value)})
                case "Strikeouts per 9 Innings":
                    player_stats.update({"K/9": safe_float(value)})
                case "Saves Plus Holds":
                    player_stats.update({"SVHD":
                                         safe_int(value) if etl_type == ETLType.PRE_SZN else
                                         safe_float(value)})

        match cat:
            case _ if re.match(".*rostered.*", cat):
                player_stats.update({"%ROST": safe_float(value)})
            case _ if re.match(".*Rating.*", cat):
                player_stats.update({"PRTR": safe_float(value)})

    return player_stats


def safe_float(text_value):
    if text_value == "--":
        return None
    else:
        return float(text_value)


def safe_int(text_value):
    if text_value == "--":
        return None
    else:
        return int(text_value)
