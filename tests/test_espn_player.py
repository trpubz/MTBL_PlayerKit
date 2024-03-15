from pathlib import Path
import json
import re
import pytest
import bs4 as bs

from mtbl_playerkit import ESPNPlayer


class TestESPNPlayer:
    @pytest.fixture
    def player_data(self):
        fixtures_path = Path(__file__).parent / "fixtures"
        player_data_path = fixtures_path / "player_data_missing_title_tag.html"
        data = ""
        with open(player_data_path, "r") as f:
            data = f.read()

        return bs.BeautifulSoup(data, "lxml").find_all("td")

    @pytest.fixture
    def bad_data(self):
        fixtures_path = Path(__file__).parent / "fixtures"
        player_data_path = fixtures_path / "player_data_no_id_missing_title_tag.html"
        data = ""
        with open(player_data_path, "r") as f:
            data = f.read()

        return bs.BeautifulSoup(data, "lxml").find_all("td")

    @pytest.fixture
    def player_dict(self):
        return {
            "name": "Ronald Acuna Jr.",
            "team": "ATL",
            "ovr": 99,
            "owner": "TeamOwner",
            "positions": ["OF"],
            "player_stats": {"AVG": ".280"},
            "espn_id": "12345",
        }

    def test_create_player(self, player_data):
        player = ESPNPlayer.from_data(player_data)

        assert player.__class__ is ESPNPlayer
        assert "Ronald" in player.name

    def test_create_player_no_float_values(self, player_data):
        player = ESPNPlayer.from_data(player_data)

        assert player.__class__ is ESPNPlayer
        assert "Ronald" in player.name
        assert player.player_stats["SLG"] is None
        assert isinstance(player.player_stats["HR"], float)

    def test_create_player_remove_rp_from_pos_player(self, player_data):
        player = ESPNPlayer.from_data(player_data)

        assert "RP" not in player.positions

    def test_create_player_no_id(self, bad_data):
        player = None
        with pytest.raises(IndexError) as e:
            player = ESPNPlayer.from_data(bad_data)

        assert e.type is IndexError
        assert player is None

    def test_create_player_no_div_title(self, player_data):
        # gracefully handle missing title tag
        player = ESPNPlayer.from_data(player_data)
        assert isinstance(player, ESPNPlayer)

    def test_serialization_to_dict(self, player_dict):
        player = ESPNPlayer(**player_dict)
        assert player.dict() == player_dict

    def test_serialization_to_json(self, player_dict):
        player = ESPNPlayer(**player_dict)
        assert json.loads(player.json()) == player_dict
