from enum import Enum
from difflib import get_close_matches


class GlobalProperty:
    """Property which shares one value for all instances."""

    def __init__(self, value):
        self.value = value

    def __get__(self, instance, owner=None):
        return self.value

    def __set__(self, instance, value):
        self.value = value



class Key(Enum):
    """Enumeration of the profile keys."""

    values = GlobalProperty(list())

    # Characteristics (Stats)
    WS  = "Weapon Skill"
    BS  = "Ballistic Skill"
    S   = "Strength"
    T   = "Toughness"
    AG  = "Agility"
    INT = "Intelligence"
    PER = "Perception"
    WP  = "Willpower"
    FEL = "Fellowship"
    IFL = "Influence"

    # Skills - note: must be declared after Stats
    ACROBATICS  = "Acrobatics", "AG"
    ATHLETICS   = "Athletics", "S"
    AWARENESS   = "Awareness", "PER"
    CHARM       = "Charm", "FEL"
    COMMAND     = "Command", "FEL"
    COMMERCE    = "Commerce", "INT"
    DECEIVE     = "Deceive", "FEL"
    DODGE       = "Dodge", "AG"
    INQUIRY     = "Inquiry", "FEL"
    INTERROGATE = "Interrogation", "WP"
    INTIMIDATE  = "Intimidate", "S"
    LOGIC       = "Logic", "INT"
    MEDICAE     = "Medicae", "INT"
    NAV_SURFACE = "Navigate Surface", "INT"
    NAV_STELLAR = "Navigate Stellar", "INT"
    NAV_WARP    = "Navigate Warp", "INT"
    OP_AERO     = "Operate Aeronautica", "AG"
    OP_SURFACE  = "Operate Surface", "AG"
    OP_VOID     = "Operate Voidship", "AG"
    PARRY       = "Parry", "WS"
    PSY         = "Psyniscience", "PER"
    SCRUTINY    = "Scrutiny", "PER"
    SECURITY    = "Security", "INT"
    SLT_OF_HAND = "Sleight of Hand", "AG"
    STEALTH     = "Stealth", "AG"
    SURVIVAL    = "Survival", "PER"
    TECH_USE    = "Tech Use", "INT"


    def __new__(cls, value, default_stat=None):

        instance = object.__new__(cls)
        instance.pretty = value
        instance._value_ = value.lower()

        cls.values.append(instance._value_) # pylint: disable=no-member

        # Initialise stat
        if default_stat is None:
            instance.stat = instance
            instance.skill = None
            instance.kind = "Stat"

        # Initialise skill
        else:
            instance.stat = cls.__members__[default_stat]
            instance.skill = instance
            instance.kind = "Skill"

        return instance

    
    @classmethod
    def get(cls, raw, fuzzy=False):
        """Safely lookup a key.
        
        Args:
            raw: The name or value of the key to lookup.
            fuzzy: Should we try to autocorrect a misspelled value?

        Notes:
            - Stats can be looked up by name or value.
            - Skills can only be looked up by value.
            - All lookups are case-insensitive.
        """

        value = raw.lower()

        # Lookup by value
        try:
            return cls(value)
        except ValueError:
            pass

        # Lookup by name (stat only)
        try:
            name = raw.upper()
            result = cls[name]
            if result.is_stat:
                return result
        except KeyError:
            pass

        if fuzzy:
            # Try to autocorrect value
            matches = get_close_matches(value, cls.values, 1)
            if matches:
                return cls(*matches)

        return None


    @classmethod
    def read_command(cls, left, right=None):
        """Return the stat/skill pair for given command pair."""

        key = Key.get(left, fuzzy=True)

        # Single stat or skill command
        if right is None:

            if key is not None:
                return key.stat, key.skill

        # Paired "skill on stat" command
        elif (
            key is not None
            and key.is_skill
        ):

            other_key = Key.get(right, fuzzy=True)
            if (
                other_key is not None
                and other_key.is_stat
            ):
                return other_key, key

        return None


    @property
    def is_stat(self):
        return self.kind == "Stat"


    @property
    def is_skill(self):
        return self.kind == "Skill"

    
    def __str__(self):
        return self.pretty


    def __repr__(self):
        return f"<{self.kind}~Key.{self.name}>"



class Attack(Enum):
    """Enumeration of possible attack types."""

    SINGLE = "Single Shot", "Single Attack", "Single Attack"
    SEMI = "Semi-Auto Burst", "Swift Attack", "Semi-Auto/Swift Attack"
    FULL = "Full-Auto Burst", "Lightning Attack", "Full-Auto/Lightning Attack"


    def __init__(self, ranged, melee, unknown):
        
        self.ranged = ranged
        self.melee = melee
        self.unknown = unknown


    def description(self, stat=None):
        """Return description for an attack."""

        if stat is Key.BS:
            return self.ranged
        elif stat is Key.WS:
            return self.melee
        else:
            return self.unknown


    @classmethod
    def decode(cls, token):

        if token == "!":
            return cls.SINGLE
        elif token == "!!":
            return cls.SEMI
        elif token == "!!!":
            return cls.FULL
        else:
            return None
