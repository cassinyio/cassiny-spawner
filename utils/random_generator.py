"""Generator of random things."""

import random
import secrets
from typing import Sequence
from uuid import UUID, uuid1

# len(_adjectives) == 91
_adjectives = (
    "aged", "ancient", "autumn", "billowing", "bitter", "black", "blue", "bold",
    "broad", "broken", "calm", "cold", "cool", "crimson", "curly", "damp",
    "dark", "dawn", "delicate", "divine", "dry", "empty", "falling", "fancy",
    "flat", "floral", "fragrant", "frosty", "gentle", "green", "hidden", "holy",
    "icy", "jolly", "late", "lingering", "little", "lively", "long", "lucky",
    "misty", "morning", "muddy", "mute", "nameless", "noisy", "odd", "old",
    "orange", "patient", "plain", "polished", "proud", "purple", "quiet", "rapid",
    "raspy", "red", "restless", "rough", "round", "royal", "shiny", "shrill",
    "shy", "silent", "small", "snowy", "soft", "solitary", "sparkling", "spring",
    "square", "steep", "still", "summer", "super", "sweet", "throbbing", "tight",
    "tiny", "twilight", "wandering", "weathered", "white", "wild", "winter", "wispy",
    "withered", "yellow", "young"
)

# len(_nouns) == 86
_nouns = (
    "delphini", "eridani", "lyncis", "draconis", "andromedae", "pegasi",
    "achernar", "aetos", "albireo", "alcyone", "aldebaran", "algol",
    "alnilam", "alnitak", "alphard", "altair", "altarf", "antares", "arcturus",
    "arion", "bellatrix", "capricorni", "ophiuchi", "betelgeuse", "camelopardalis",
    "canis", "canopus", "capella", "capricornus", "caracal", "centaurus",
    "cithara", "columba", "caroli", "corvus", "crux", "delphinus", "deneb",
    "denebola", "dolphin", "eagle", "epsilon", "propus", "fomalhaut", "gacrux",
    "velorum", "grissom", "hamal", "hare", "helveti", "horus", "superba",
    "lambda", "shu", "lyra", "medina", "meissa", "meissa", "heka", "mintaka",
    "mira", "ogma", "phecda", "piscis", "austrinus", "pleiades", "polaris",
    "procyon", "proxima", "centauri", "puppis", "regulus", "rigel", "saif",
    "saiph", "sapphire", "scorpius", "sirius", "sopdet", "spica", "scorpii",
    "taygeta", "thuban", "ursa", "vega", "scorpii"
)


def naminator(name_type: str, *, delimiter: str = "-",
              token_length: int = 4, token_hex: bool = False) -> str:
    """
    Generate heroku-like random names to use in your python applications
    :param delimiter: Delimiter
    :param token_length: TokenLength
    :param token_hex: TokenHex
    :param token_chars: TokenChars
    :type delimiter: str
    :type token_length: int
    :type token_hex: bool
    :type token_chars: str
    :return: heroku-like random string
    :rtype: str
    """

    correct_type = {"api", "probe", "job", "cargo"}
    if name_type not in correct_type:
        raise TypeError(
            f"name_type should be either `api`, `probe`, `job` or `cargo`, passed: {name_type}")

    token_chars = "0123456789"

    if token_hex:
        token_chars = "0123456789abcdef"

    # select a random value from _adjectives and _nouns and create a tuple
    values = _random_element(_adjectives), _random_element(_nouns)
    name = "".join(values)
    token = "".join(_random_element(token_chars) for _ in range(token_length))

    sections = (name_type, name, token)
    return delimiter.join(filter(None, sections))


def _random_element(strings: Sequence[str]) -> str:
    """
    Get random element from string or list
    :param s: Element
    :type s: str or list
    :return: str
    :rtype: str
    """

    return secrets.choice(strings)


def get_uuid() -> UUID:
    """Return a UUID1 with a random node."""
    return uuid1((random.getrandbits(48) | 0x010000000000))
