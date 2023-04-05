from pipster._experimental.autoinstall import _get_deps


def test_get_deps():
    assert _get_deps("tests/data/imports.py") == [
        ("bs4", ("beautifulsoup4",)),
        ("libcst", None),
        ("sklearn", ("scikit-learn",)),
        ("requests", None),
        ("numpy", None),
        ("pandas", None),
    ]
