from pathlib import Path
import pytest


class TestPlayerFactory:
    @pytest.fixture
    def player_data(self):
        fixtures_path = Path(__file__).parent / "fixtures"
        player_data_path = fixtures_path / "player_data.html"
        with open(player_data_path, "r") as f:
            return f.read()

    def test_create_espn_player(self, player_data):
        pass
