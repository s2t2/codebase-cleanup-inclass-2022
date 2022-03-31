
from app.utils import to_usd


def test_to_usd():
    assert to_usd(0.459) == "$0.46"
    assert to_usd(23.2222) == "$23.22"
    assert to_usd(1234567890.999999) == "$1,234,567,891.00"
