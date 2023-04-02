from importlib import import_module

import pytest

from pipster.install import _build_install_cmd
from pipster.install import _get_dist_name
from pipster import install

TEST_PKG = "realpython-reader"
TEST_PKG_A = TEST_PKG + "==0.0.1"
TEST_PKG_B = TEST_PKG + "==1.1.1"
TEST_MODULE = "reader"

WHEEL_PATH = "tests/data/packages/"
WHEEL1 = WHEEL_PATH + "simplewheel-1.0-py2.py3-none-any.whl"
WHEEL2 = WHEEL_PATH + "simplewheel-2.0-py2.py3-none-any.whl"


"""
TODO implement the following tests

install(wheel1, target="/tmp//")
install(wheel2, target="/tmp//", upgrade=True)
"""


def test_build_install_cmd_plain():
    io_pairs = [
        ("pip install some_pkg", ["pip", "install", "some_pkg"]),
        ("some_pkg", ["pip", "install", "some_pkg"]),
        (
            "pip install --user some_pkg",
            ["pip", "install", "--user", "some_pkg"],
        ),  # noqa: E501
        (
            "pip install -r requirements.txt",
            ["pip", "install", "-r", "requirements.txt"],
        ),  # noqa: E501
        (
            "pip install --target /tmp//dir_without_spaces /path/to/wheel",
            [
                "pip",
                "install",
                "--target",
                "/tmp//dir_without_spaces",
                "/path/to/wheel",
            ],
        ),  # noqa: E501
        (
            "pip install --target '/tmp//dir with spaces' /path/to/wheel",
            ["pip", "install", "--target", "/tmp//dir with spaces", "/path/to/wheel"],
        ),  # noqa: E501
    ]
    for arg, output in io_pairs:
        cmd = _build_install_cmd(arg)
        assert cmd == output


def test_build_install_cmd_kwarg():
    assert _build_install_cmd(r="requirements.txt") == [
        "pip",
        "install",
        "-r",
        "requirements.txt",
    ]
    assert _build_install_cmd("some_pkg", user=True) == [
        "pip",
        "install",
        "--user",
        "some_pkg",
    ]


def test__get_dist_name():
    assert _get_dist_name(WHEEL1) == "simplewheel"
    assert _get_dist_name(WHEEL2) == "simplewheel"
    assert _get_dist_name(TEST_PKG_A) == "realpython-reader"
    assert _get_dist_name(TEST_PKG_B) == "realpython-reader"


def test_build_install_cmd_underscores():
    # find_links -> --find-links
    assert _build_install_cmd("some_pkg", find_links="/local/dir/") == [
        "pip",
        "install",
        "--find-links",
        "/local/dir/",
        "some_pkg",
    ]


def test_install_simplewheel():
    result1 = install(WHEEL1)
    assert result1.returncode == 0
    result2 = install(WHEEL2)
    assert result2.returncode == 0


def test_already_loaded():
    result1 = install(WHEEL1)
    assert result1.returncode == 0
    import simplewheel  # type: ignore  # noqa: F401

    with pytest.warns(UserWarning):
        result2 = install(WHEEL2)
        assert result2.returncode == 0


def test_ptp_already_loaded_warning():
    # requires internet connection
    install(TEST_PKG_A)
    import_module(TEST_MODULE)
    with pytest.warns(UserWarning):
        result = install(TEST_PKG_B)
        assert result.returncode == 0


def test_ptp_already_loaded_warning_upgradeTrue():
    # requires internet connection
    install(TEST_PKG_A)
    import_module(TEST_MODULE)
    with pytest.warns(UserWarning):
        result = install(TEST_PKG_B, upgrade=True)
        assert result.returncode == 0
