

def test_ramp_loading1():
    from ..ramp import Loader
    assert Loader().load() is not None


def test_ramp_loading2():
    from ..ramp_min import Loader
    assert Loader().load() is not None


def test_ramp_loading3():
    from ..ramp_large import Loader
    assert Loader().load() is not None


def test_pgp_loading():
    from ..pgp import Loader
    assert Loader().load() is not None


def test_infovis_loading():
    from ..infovis import Loader
    assert Loader().load() is not None
