from random import randint
from math import ceil, floor
from discord import Color

from ..enums import Attack, Key
from .locations import locations


def d(N, tearing=False):
    """Return roll of a fair N-sided die.
    
    Args:
        N: Number of faces on die.
        tearing: If tearing, we roll twice and take the highest.
    """

    roll = randint(1, N)
    if tearing:
        roll = max(roll, randint(1, N))

    return roll


def test(target):
    """Perform test with given target, returning raw roll and degrees of success."""

    roll = randint(1, 100)

    difference = target - roll

    if difference >= 0:
        degrees = ceil((difference + 1) / 10)
        if roll == 1:
            degrees += 1
        elif roll == 100:
            degrees = -1
    else:
        degrees = floor((difference - 1) / 10)
        if roll == 100:
            degrees -= 1
        elif roll == 1:
            degrees = 1

    return roll, degrees


def make_hint(stat, skill, attack):
    """Generate short test description."""

    # Hints for stat and skill tests
    if stat is None:
        hint = None
    elif skill is None:
        hint = str(stat)
    else:
        hint = f"{skill} on {stat}"

    # Extended hints for attack tests
    if attack is not None:
        attack_hint = attack.description(stat)

        # Prepend to normal hint
        if (
            hint is None
            or (
                skill is None
                and (
                    stat is Key.WS
                    or stat is Key.BS
                )
            )
        ):
            hint = attack_hint
        else:
            hint = f"{attack_hint} ({hint})"

    return hint


def clamp(value, minimum=-60, maximum=60):
    """Return value restricted to the range [minimum, maximum]."""

    return max(minimum, min(maximum, value))


def hit_description(roll, degrees, attack):
    """Generate description of hits for an attack roll."""

    if degrees <= 0:
        return "Missed"

    if attack is Attack.SEMI:
        hits = (degrees + 1) // 2
    elif attack is Attack.FULL:
        hits = degrees
    else:
        return f"Hit: `{locations(roll)}`"
    
    return f"Hits: `{hits}` = " + ", ".join(f"`{place}`" for place in locations(roll, hits))


def describe_one(roll, degrees, attack, pad):
    """Generate description of degree and hits for a roll."""

    num = abs(degrees)
    # success = "success" if degrees > 0 else "failure"
    # s = "s" if num > 1 else ""
    sign = "+" if degrees > 0 else "-"

    roll_text = f"Roll: `{roll:{pad}}` | Degrees: `{sign}{num}`"
    
    # Extra text for attacks
    if (
        attack is not None
    ):
        return f"{roll_text} | {hit_description(roll, degrees, attack)}"
    else:
        return roll_text


def describe(target, rolls, attack):
    """Generate full description of one or more rolls."""

    description = f"Target: `{target}`"

    if len(rolls) > 1:
        description += "\n――――――\n"
    else:
        description += " | "

    # Determine roll padding
    highest = max(roll for roll, _ in rolls)
    if highest == 100:
        pad = 3
    elif highest >= 10:
        pad = 2
    else:
        pad = 1

    return description + "\n".join(
        describe_one(roll, degrees, attack, pad) for roll, degrees in rolls
    )


def colour(rolls):
    """Return Discord embed colouring for given rolls."""

    if len(rolls) > 1:
        return Color.blue()
    elif rolls[0][1] > 0:
        return Color.green()
    else:
        return Color.red()



class SkillTest:
    """Class for representing Dark Heresy roll requests."""
    
    def __init__(self, modifier=0, stat=None, skill=None, attack=None, repeats=1, profile_name=None):
        """Create a roll request.
        
        Args:
            modifier: Sum of modifiers for the test.
            stat: Characteristic to be rolled on.
            skill: Skill being tested.
            attack: Attack mode.
            repeats: Number of times to repeat the test.

        Notes:
            - If no skill is provided, do simple characteristic test.
            - If no stat or skill is provided, do simple test using modifier as target.
        """

        self.modifier = modifier
        self.stat = stat
        self.skill = skill
        self.attack = attack
        self.repeats = repeats
        self.hint = make_hint(stat, skill, attack)
        self.is_complex = bool(skill or stat)
        self.profile_name = profile_name


    def get_target(self, profile):
        """Return roll target for given profile."""

        base = 0
        modifier = self.modifier

        if self.skill is not None:
            modifier += profile.get(self.skill, -20)

        if self.stat is not None:
            base += profile.get(self.stat, 30)
            modifier = clamp(modifier)

        return base + modifier


    def roll(self, profile):
        """Perform roll for given profile."""

        target = self.get_target(profile)
        rolls = [test(target) for _ in range(self.repeats)]

        return target, rolls


    def __call__(self, profile=None):
        """Perform and format roll for given profile."""

        if (
            self.is_complex
            and profile is None
        ):
            return None

        target, rolls = self.roll(profile)        
        response = {
            "description": describe(target, rolls, self.attack),
            "footer": self.hint,
            "color": colour(rolls)
        }

        if profile is not None:
            response["profile"] = profile.long_name
        
        return response



class DiceTerm:
    """Class for representing a dice term in a dice equation."""

    def __init__(self, number, sides, tearing, sign=1):

        self.number = number
        self.sides = sides
        self.tearing = tearing
        self.sign = sign

    
    def roll(self, profile=None):

        total = 0
        descriptions = list()
        crit = False
        
        for _ in range(self.number):

            roll = d(self.sides, self.tearing)

            total += roll

            # Check for critical rolls
            if (
                self.sides == roll == 10
                or (
                    self.sides == roll == 5
                    and randint(1, 2) == 2
                )
            ):
                crit = True
                descriptions.append(f"{roll}!")
            else:
                descriptions.append(str(roll))

        description = ", ".join(descriptions)

        total *= self.sign

        return total, self.sign,  f"[{description}] ({self.number}d{self.sides}{'T' if self.tearing else ''})", crit



class BonusTerm:
    """Class for representing a stat bonus term in a dice equation."""

    def __init__(self, stat, sign):

        self.stat = stat
        self.sign = sign


    def roll(self, profile):

        bonus = profile.get(self.stat, 30) // 10
        total = bonus * self.sign

        return total, self.sign, f"{total} ({self.stat.name}B)", False



class DiceEquation:
    """Class for representing dice equations."""

    def __init__(self, terms):
        """Create a dice equation."""

        self.flat = 0
        self.terms = list()
        self.dice_count = 0
        self.is_complex = False
        self.profile_name = None

        for term in terms:
            if isinstance(term, int):
                self.flat += term
            elif isinstance(term, DiceTerm):
                self.terms.append(term)
                self.dice_count += term.number
            else:
                self.terms.append(term)
                self.is_complex = True



    def __call__(self, profile=None):
        """Perform and format roll."""

        if (
            self.is_complex
            and profile is None
        ):
            return None

        total = self.flat
        description = "" 
        critical = False

        for term in self.terms:
            
            value, sign, text, crit = term.roll(profile)

            total += value
            critical |= crit

            if description:
                description += " + " if sign == 1 else " - "
            elif sign == -1:
                description += "-"
            
            description += text

        if self.flat != 0:
            description += f" {'+' if self.flat > 0 else '-'} {abs(self.flat)}"

        response = {
            "description": f"Rolls: `{description}` | Total: `{total}`",
            "color": Color.gold() if critical else Color.light_gray(),
            "footer": "Critical Damage" if critical else None
        }

        if profile is not None:
            response["profile"] = profile.long_name

        return response
