from random import sample


def generator(*args, final):
    yield from args
    while True:
        yield final


def left_right():
    return sample(["L", "R"], k=2)


TABLE = {
    "Head": lambda A, B: generator("Head", "Head", f"{A}-Arm", "Body", f"{B}-Arm", final="Body"),
    "Body": lambda A, B: generator("Body", "Body", f"{A}-Arm", "Head", f"{B}-Arm", final="Body"),
    "Left Arm": lambda A, B: generator("L-Arm", "L-Arm", "Body", "Head", "Body", final=f"{A}-Arm"),
    "Right Arm": lambda A, B: generator("R-Arm", "R-Arm", "Body", "Head", "Body", final=f"{A}-Arm"),
    "Left Leg": lambda A, B: generator("L-Leg", "L-Leg", "Body", f"{A}-Arm", "Head", final="Body"),
    "Right Leg": lambda A, B: generator("R-Leg", "R-Leg", "Body", f"{A}-Arm", "Head", final="Body")
}


def initial_location(roll):
    """Return initial hit location for a given roll."""

    if roll < 100:
        roll = (roll // 10) + (10 * (roll % 10))
    if roll > 30:
        if roll <= 70:
            return "Body"
        elif roll <= 85:
            return "Right Leg"
        else:
            return "Left Leg"
    elif roll <= 10:
        return "Head"
    elif roll <= 20:
        return "Right Arm"
    else:
        return "Left Arm"


def locations(roll, hits=None):
    """Return hit locations for a given roll."""
    
    initial = initial_location(roll)

    if hits is None:
        return initial

    first, second = left_right()

    iterator = TABLE[initial](first, second)

    return [next(iterator) for _ in range(hits)]