from events.service import (
    get_service_status,
    get_service_type,
)
from utils import naminator


def test_get_service_type():
    service_type = "probe"
    name = naminator(service_type)
    assert get_service_type(name) == service_type


def test_service_status():
    assert get_service_status("probe", 'start', None) == 1
    assert get_service_status("cargo", 'destroy', None) == 4
    assert get_service_status("job", 'die', '0') == 2
    assert get_service_status("job", 'die', '1') == 3
    assert get_service_status("starship", 'start', None) is False
