from pathlib import Path
import pytest

from mtbl_playerkit import ESPNPlayer
from mtbl_playerkit.player_factory import PlayerFactory


class TestPlayerFactory:
    @pytest.fixture
    def players_data(self):
        fixtures_path = Path(__file__).parent / "fixtures"
        player_data_path = fixtures_path / "players_data.html"
        with open(player_data_path, "r") as f:
            return f.read()

    def test_create_espn_player(self, players_data):
        players = PlayerFactory.create_players("ESPN", players_data)
        assert len(players) > 0
        assert players[0].__class__ is ESPNPlayer
        assert isinstance(players, list)

    def test_create_player_bad_source(self, players_data):
        with pytest.raises(ValueError) as e:
            players = PlayerFactory.create_players("BAD_SOURCE", players_data)

        assert e.type is ValueError
