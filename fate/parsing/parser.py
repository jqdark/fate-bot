from lark import Lark
from lark.visitors import Transformer
from lark.exceptions import LarkError

from .rolls import SkillTest, DiceTerm, BonusTerm, DiceEquation
from ..enums import Key, Attack


class Processor(Transformer):
    """Transformer for the FateBot grammar.
    
    Takes a parse tree and transforms it into a SkillTest or DiceEquation instance.
    """

    def test_start(self, args):
        """Entry point for reading skill test parse tree."""

        return args[0]


    def test(self, args):

        profile_name, command, *terms, attack, repeats = args

        stat = None
        skill = None
        modifier = sum(terms)
        attack = Attack.decode(attack)
        repeats = 1 if repeats is None else int(repeats)

        if repeats > 30:
            ## TODO Rework this
            raise LarkError

        if isinstance(command, int):
            modifier += command
        else:
            stat, skill = command
        
        return SkillTest(modifier, stat, skill, attack, repeats, profile_name)


    def command(self, args):

        pair = Key.read_command(*args)
        
        if pair is None:
            raise LarkError
        
        return pair


    def term(self, args):

        sign, number = args
        if sign == "-":
            return -int(number)
        else:
            return int(number)


    def PROFILE(self, token):

        # Strip leading "#"
        return token.update(value=token[1:])


    def MACRO(self, token):

        # Strip leading "="
        return token.update(value=token[1:])

    
    def dice_start(self, args):
        """Entry point for reading dice equation parse tree."""

        *terms, repeats = args

        repeats = 1 if repeats is None else int(repeats)

        request = DiceEquation(terms, repeats)

        # TODO Need a more transparent solution
        if request.dice_count > 200:
            raise LarkError

        return request


    def dice_term(self, args):
        
        sign, value = args

        sign = -1 if sign == "-" else 1

        if isinstance(value, DiceTerm):
            value.sign *= sign
            return value
        elif isinstance(value, Key):
            return BonusTerm(value, sign)
        else:
            return int(value) * sign


    def dice(self, args):

        number, sides, tearing = args

        sides = int(sides)
        tearing = (tearing is not None)

        if number is None:
            number = 1
        else:
            number = int(number)

        return DiceTerm(number, sides, tearing)


    def bonus(self, args):

        raw = args[0].upper()

        try:
            key = Key[raw]
            if key.is_stat:
                return key
        except ValueError:
            pass

        raise LarkError


    def STAT_BONUS(self, token):

        # Strip trailing "B"
        return token.update(value=token[:-1])



class Parser:
    """Parsing class for the FateBot grammar."""

    def __init__(self, debug=False):

        self.debug = debug
        self.parser = Lark.open("fate.lark", __file__,
            start=["test_start", "dice_start"],
            parser="lalr",
            maybe_placeholders=True,
            transformer=Processor()
        )

    
    def _parse(self, raw, start):
        """Parse input string raw from specified start rule."""

        try:
            return self.parser.parse(raw, start=start)
        except LarkError as error:
            if self.debug: print(error)
            return None

    
    def parse(self, raw):
        """Parse input string raw."""

        return (
            self._parse(raw, "test_start") or
            self._parse(raw, "dice_start")
        )

