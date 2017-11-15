
import re

from utils.name_generator import naminator


def test_general_functionality():
    regex = re.compile('[a-z]+-[a-z]+-[0-9]{4}$')
    name = naminator("api")
    assert regex.match(name), name


def test_wont_return_same_name():
    assert naminator("api") != naminator("api")
