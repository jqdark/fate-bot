from fate.enums import Key


class TestKey:

    def test_get(self):

        # Correct lookups
        assert Key.get("ws") is Key.WS
        assert Key.get("weapon Skill") is Key.WS
        assert Key.get("parry") is Key.PARRY
        assert Key.get("sleight OF hand") is Key.SLT_OF_HAND

        # Wrong lookups
        assert Key.get("athletes") is None
        assert Key.get("NAV_SURFACE") is None
        assert Key.get("AG ") is None
        assert Key.get("psy") is None
        assert Key.get("Tech-Use") is None

        # Fuzzy lookups
        assert Key.get("Tech-Use", fuzzy=True) is Key.TECH_USE
        assert Key.get("Will POWER", fuzzy=True) is Key.WP
        assert Key.get("AAA?????????zzzzzzz", fuzzy=True) is None


    def test_read_command(self):
        
        stat, skill = Key.read_command("STEALTH")
        assert stat is Key.AG
        assert skill is Key.STEALTH

        stat, skill = Key.read_command("athletics", "WP")
        assert stat is Key.WP
        assert skill is Key.ATHLETICS

        # Correctable fuzzy
        stat, skill = Key.read_command("strngth")
        assert stat is Key.S
        assert skill is None

        # Uncorrectable fuzzy
        assert Key.read_command("AAAAaaabbbbbbbbb#####") is None
        assert Key.read_command("AAA123ZZZZZZZZZA123AA", "bs") is None
        assert Key.read_command("commerce", "                  ") is None

        # Invalid pairings
        assert Key.read_command("strength", "strength") is None
        assert Key.read_command("wp", "stealth") is None