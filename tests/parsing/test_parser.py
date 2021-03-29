import pytest

from fate.parsing.parser import Parser
from fate.enums import Key, Attack


class TestParser:

    @pytest.fixture
    def parser(self):
        return Parser()


    @pytest.mark.parametrize(["command", "expected"], [
        ("=gun", "gun"),
        ("=MED009", "MED009"),
        ("athletics on agility +20", {
            "skill": Key.ATHLETICS,
            "stat": Key.AG,
            "modifier": 20,
            "attack": None,
            "repeats": 1,
            "profile_name": None
        }),
        ("AFeltics on Ag", {
            "skill": Key.ATHLETICS,
            "stat": Key.AG,
            "modifier": 0,
            "attack": None,
            "repeats": 1,
            "profile_name": None
        }),
        (" 10  +20-5+3 +17", {
            "skill": None,
            "stat": None,
            "modifier": 45,
            "attack": None,
            "repeats": 1,
            "profile_name": None
        }),
        ("  #Other \t\n +30 -50", {
            "skill": None,
            "stat": None,
            "modifier": -20,
            "attack": None,
            "repeats": 1,
            "profile_name": "Other"
        }),
        (" agility !! * 11 ", {
            "skill": None,
            "stat": Key.AG,
            "modifier": 0,
            "attack": Attack.SEMI,
            "repeats": 11,
            "profile_name": None
        }),
        (" #bob parry on weapon skill + 20 !!! ", {
            "skill": Key.PARRY,
            "stat": Key.WS,
            "modifier": 20,
            "attack": Attack.FULL,
            "repeats": 1,
            "profile_name": "bob"
        })
    ])
    def test_parse(self, parser, command, expected):

        result = parser.parse(command)

        if isinstance(result, str):
            assert result == expected
        else:
            for key, value in expected.items():
                assert getattr(result, key) == value