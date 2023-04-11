# from importlib import import_module
import re

from pipster.install import _build_install_cmd
from pipster.install import _get_dist_name
from pipster.install import _get_requirements_from_file
from pipster.install import _install

TEST_PKG = "realpython-reader"
TEST_PKG_A = TEST_PKG + "==0.0.1"
TEST_PKG_B = TEST_PKG + "==1.1.1"
TEST_MODULE = "reader"

WHEEL_PATH = "tests/data/packages/"
WHEEL1 = WHEEL_PATH + "simplewheel-1.0-py2.py3-none-any.whl"
WHEEL2 = WHEEL_PATH + "simplewheel-2.0-py2.py3-none-any.whl"

REQ_FILE = "tests/data/requirements.txt"


"""
TODO implement the following tests

_install(wheel1, target="/tmp//")
_install(wheel2, target="/tmp//", upgrade=True)
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
    row_re = r"\|\s*`(.*?)`\s*\|\s*`(.*?)`\s*\|\s*$"
    with open("cli_options.md") as f:
        table_lines = [line for line in f if line.startswith("|")]
    option_lines = [line for line in table_lines if re.match(row_re, line)]
    assert len(option_lines) == len(table_lines) - 2
    for line in option_lines:
        cli_opt, kwarg = re.match(row_re, line).groups()
        evaluated = eval(f"_build_install_cmd({kwarg})")
        assert " ".join(evaluated[2:]) == cli_opt


def test__get_dist_name():
    assert _get_dist_name(WHEEL1) == "simplewheel"
    assert _get_dist_name(WHEEL2) == "simplewheel"
    assert _get_dist_name(TEST_PKG_A) == "realpython-reader"
    assert _get_dist_name(TEST_PKG_B) == "realpython-reader"
    urls = [  # from https://pip.pypa.io/en/stable/topics/vcs-support/
        "git+ssh://git.example.com/MyProject#egg=MyProject",
        "git+file:///home/user/projects/MyProject#egg=MyProject",
        "git+https://git.example.com/MyProject#egg=MyProject",
        "git+https://git.example.com/MyProject.git@master#egg=MyProject",
        "git+https://git.example.com/MyProject.git@v1.0#egg=MyProject",
        "git+https://git.example.com/MyProject.git@da39a3ee5e6b4b0d3255bfef95601890afd80709#egg=MyProject",
        "git+https://git.example.com/MyProject.git@refs/pull/123/head#egg=MyProject",
        "hg+http://hg.myproject.org/MyProject#egg=MyProject",
        "hg+https://hg.myproject.org/MyProject#egg=MyProject",
        "hg+ssh://hg.myproject.org/MyProject#egg=MyProject",
        "hg+file:///home/user/projects/MyProject#egg=MyProject",
        "hg+http://hg.example.com/MyProject@da39a3ee5e6b#egg=MyProject",
        "hg+http://hg.example.com/MyProject@2019#egg=MyProject",
        "hg+http://hg.example.com/MyProject@v1.0#egg=MyProject",
        "hg+http://hg.example.com/MyProject@special_feature#egg=MyProject",
        "svn+https://svn.example.com/MyProject#egg=MyProject",
        "svn+ssh://svn.example.com/MyProject#egg=MyProject",
        "svn+ssh://user@svn.example.com/MyProject#egg=MyProject",
        "svn+http://svn.example.com/svn/MyProject/trunk@2019#egg=MyProject",
        "svn+http://svn.example.com/svn/MyProject/trunk@{20080101}#egg=MyProject",
        "bzr+http://bzr.example.com/MyProject/trunk#egg=MyProject",
        "bzr+sftp://user@example.com/MyProject/trunk#egg=MyProject",
        "bzr+ssh://user@example.com/MyProject/trunk#egg=MyProject",
        "bzr+ftp://user@example.com/MyProject/trunk#egg=MyProject",
        # "bzr+lp:MyProject#egg=MyProject",  # TODO
        "bzr+https://bzr.example.com/MyProject/trunk@2019#egg=MyProject",
        "bzr+http://bzr.example.com/MyProject/trunk@v1.0#egg=MyProject",
        "MyProject @ git+ssh://git.example.com/MyProject",
        "MyProject @ git+file:///home/user/projects/MyProject",
        "MyProject @ git+https://git.example.com/MyProject",
        "MyProject @ git+https://git.example.com/MyProject.git@master",
        "MyProject @ git+https://git.example.com/MyProject.git@v1.0",
        "MyProject @ git+https://git.example.com/MyProject.git@da39a3ee5e6b4b0d3255bfef95601890afd80709",
        "MyProject @ git+https://git.example.com/MyProject.git@refs/pull/123/head",
        "MyProject @ hg+http://hg.myproject.org/MyProject",
        "MyProject @ hg+https://hg.myproject.org/MyProject",
        "MyProject @ hg+ssh://hg.myproject.org/MyProject",
        "MyProject @ hg+file:///home/user/projects/MyProject",
        "MyProject @ hg+http://hg.example.com/MyProject@da39a3ee5e6b",
        "MyProject @ hg+http://hg.example.com/MyProject@2019",
        "MyProject @ hg+http://hg.example.com/MyProject@v1.0",
        "MyProject @ hg+http://hg.example.com/MyProject@special_feature",
        "MyProject @ svn+https://svn.example.com/MyProject",
        "MyProject @ svn+ssh://svn.example.com/MyProject",
        "MyProject @ svn+ssh://user@svn.example.com/MyProject",
        "MyProject @ svn+http://svn.example.com/svn/MyProject/trunk@2019",
        "MyProject @ svn+http://svn.example.com/svn/MyProject/trunk@{20080101}",
        "MyProject @ bzr+http://bzr.example.com/MyProject/trunk",
        "MyProject @ bzr+sftp://user@example.com/MyProject/trunk",
        "MyProject @ bzr+ssh://user@example.com/MyProject/trunk",
        "MyProject @ bzr+ftp://user@example.com/MyProject/trunk",
        # "MyProject @ bzr+lp:MyProject",  # TODO
        "MyProject @ bzr+https://bzr.example.com/MyProject/trunk@2019",
        "MyProject @ bzr+http://bzr.example.com/MyProject/trunk@v1.0",
        "vcs+protocol://repo_url/#egg=MyProject&subdirectory=pkg_dir",
        "vcs+protocol://repo_url/#subdirectory=pkg_dir&egg=MyProject",
        "vcs+protocol://repo_url/#subdirectory=pkg_dir&egg=MyProject&",
    ]
    for url in urls:
        assert _get_dist_name(url) == "MyProject"
    assert _get_dist_name("MyProject @ path/to/MyProject_directory") == "MyProject"
    assert _get_dist_name("MyProject @ /path/to/MyProject_directory") == "MyProject"


def test__get_requirements_from_file():
    reqs = _get_requirements_from_file(REQ_FILE)
    assert reqs == [
        "pytest",
        "pytest-cov",
        "beautifulsoup4",
        "docopt == 0.6.1",
        'requests [security] >= 2.8.1, == 2.8.* ; python_version < "2.7"',
        "urllib3 @ https://github.com/urllib3/urllib3/archive/refs/tags/1.26.8.zip",
        "MyProject~=4.0.1",
        "other-pkg",
        "MyProject>=4.0.0",
        "./downloads/numpy-1.9.2-cp34-none-win32.whl",
        "http://wxpython.org/Phoenix/snapshot-builds/wxPython_Phoenix-3.0.3.dev1820+49a8884-cp34-none-win_amd64.whl",
    ]
    dist_names = [_get_dist_name(r) for r in reqs]
    assert dist_names == [
        "pytest",
        "pytest-cov",
        "beautifulsoup4",
        "docopt",
        "requests",
        "urllib3",
        "MyProject",
        "other-pkg",
        "MyProject",
        "numpy",
        "wxpython-phoenix",
    ]


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
    result1 = _install(WHEEL1)
    assert result1.returncode == 0
    result2 = _install(WHEEL2)
    assert result2.returncode == 0


def test_already_loaded(capsys):
    result1 = _install(WHEEL1)
    assert result1.returncode == 0
    import simplewheel  # type: ignore  # noqa: F401

    result2 = _install(WHEEL2)
    captured = capsys.readouterr()
    assert result2.returncode == 0
    assert "WARNING" in captured.out


# def test_ptp_already_loaded_warning():
#     # requires internet connection
#     _install(TEST_PKG_A)
#     import_module(TEST_MODULE)
#     with pytest.warns(UserWarning):
#         result = _install(TEST_PKG_B)
#         assert result.returncode == 0
#
#
# def test_ptp_already_loaded_warning_upgradeTrue():
#     # requires internet connection
#     _install(TEST_PKG_A)
#     import_module(TEST_MODULE)
#     with pytest.warns(UserWarning):
#         result = _install(TEST_PKG_B, upgrade=True)
#         assert result.returncode == 0
