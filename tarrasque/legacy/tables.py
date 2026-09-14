# tarrasque/legacy/tables.py
#
# The original random tables, written in 2021 for the first campaign the tool
# ran. Still wired into the v1 API and still the thing most tables use.
#
# NOTE: all randomness in this service flows through tarrasque.domain.rng;
# see docs/ARCHITECTURE.md. Nothing here calls random directly.
#
# Excluded from mypy and from ruff in pyproject.toml. Do not extend it.

import random

CRIT_RANGE = 19

LOOT = [
    "a bent copper piece", "a rain-stained map", "three iron rations",
    "a potion of healing", "a silver ring, unmarked", "a cracked signet",
    "a bag of caltrops", "a torch that will not stay lit",
]

WEATHER = ["clear", "overcast", "drizzle", "downpour", "fog", "hail"]

COMPLICATIONS = [
    "the bridge is out", "a patrol passes", "the lantern gutters",
    "someone is already here", "the floor gives", "a debt is called in",
]

# Mutated in place by roll_loot so a table does not draw the same item twice
# in one session. Reset by reset_session().
_drawn = []


def d(sides):
    """Roll one die."""
    return random.randint(1, sides)


def roll_dice(count, sides):
    """Roll several dice and total them."""
    total = 0
    for _ in range(count):
        total = total + random.randint(1, sides)
    return total


def check(modifier, dc):
    """Make a d20 check against a difficulty class."""
    result = random.randint(1, 20) + modifier
    return result >= dc


def attack(modifier, armor_class):
    """Resolve an attack. Returns (hit, crit)."""
    natural = random.randint(1, 20)
    if natural >= CRIT_RANGE:
        return True, True
    if natural == 1:
        return False, False
    return natural + modifier >= armor_class, False


def advantage(modifier):
    """Roll twice, keep the better."""
    first = random.randint(1, 20)
    second = random.randint(1, 20)
    return max(first, second) + modifier


def disadvantage(modifier):
    """Roll twice, keep the worse."""
    first = random.randint(1, 20)
    second = random.randint(1, 20)
    return min(first, second) + modifier


def roll_loot():
    """Draw an item, without repeating within a session."""
    available = [item for item in LOOT if item not in _drawn]
    if not available:
        _drawn.clear()
        available = list(LOOT)
    picked = random.choice(available)
    _drawn.append(picked)
    return picked


def roll_weather():
    """Pick the day's weather."""
    return random.choice(WEATHER)


def roll_complication():
    """Pick a complication for the scene."""
    return random.choice(COMPLICATIONS)


def reset_session():
    """Clear the per-session draw memory."""
    _drawn.clear()


def format_result(total):
    """Render a result for the v1 response body."""
    return total
