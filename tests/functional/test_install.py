# from importlib import import_module

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
    man_page_args = [
        (_build_install_cmd(abi="<abi>"), "--abi <abi>"),
        (_build_install_cmd(abi=["<abi1>", "<abi2>"]), "--abi <abi1> --abi <abi2>"),
        (_build_install_cmd(break_system_packages=True), "--break-system-packages"),
        (_build_install_cmd(c="<file>"), "-c <file>"),
        (_build_install_cmd(c=["<file1>", "<file2>"]), "-c <file1> -c <file2>"),
        (_build_install_cmd(cache_dir="<dir>"), "--cache-dir <dir>"),
        (_build_install_cmd(cert="<path>"), "--cert <path>"),
        (
            _build_install_cmd(check_build_dependencies=True),
            "--check-build-dependencies",
        ),
        (_build_install_cmd(client_cert="<path>"), "--client-cert <path>"),
        (_build_install_cmd(compile=True), "--compile"),
        (
            _build_install_cmd(config_settings="<settings>"),
            "--config-settings <settings>",
        ),
        (
            _build_install_cmd(config_settings=["<settings1>", "<settings2>"]),
            "--config-settings <settings1> --config-settings <settings2>",
        ),
        (_build_install_cmd(constraint="<file>"), "--constraint <file>"),
        (
            _build_install_cmd(constraint=["<file1>", "<file2>"]),
            "--constraint <file1> --constraint <file2>",
        ),
        (_build_install_cmd(debug=True), "--debug"),
        (
            _build_install_cmd(disable_pip_version_check=True),
            "--disable-pip-version-check",
        ),
        (_build_install_cmd(dry_run=True), "--dry-run"),
        (_build_install_cmd(e="<path/url>"), "-e <path/url>"),
        (_build_install_cmd(editable="<path/url>"), "--editable <path/url>"),
        (_build_install_cmd(exists_action="<action>"), "--exists-action <action>"),
        (_build_install_cmd(extra_index_url="<url>"), "--extra-index-url <url>"),
        (_build_install_cmd(f="<url>"), "-f <url>"),
        (_build_install_cmd(find_links="<url>"), "--find-links <url>"),
        (_build_install_cmd(force_reinstall=True), "--force-reinstall"),
        (_build_install_cmd(global_option="<options>"), "--global-option <options>"),
        (_build_install_cmd(h=True), "-h"),
        (_build_install_cmd(help=True), "--help"),
        (_build_install_cmd(I=True), "-I"),
        (_build_install_cmd(i="<url>"), "-i <url>"),
        (_build_install_cmd(ignore_installed=True), "--ignore-installed"),
        (_build_install_cmd(ignore_requires_python=True), "--ignore-requires-python"),
        (
            _build_install_cmd(implementation="<implementation>"),
            "--implementation <implementation>",
        ),
        (_build_install_cmd(index_url="<url>"), "--index-url <url>"),
        (_build_install_cmd(install_option="<options>"), "--install-option <options>"),
        (_build_install_cmd(isolated=True), "--isolated"),
        (_build_install_cmd(log="<path>"), "--log <path>"),
        (
            _build_install_cmd(no_binary="<format_control>"),
            "--no-binary <format_control>",
        ),
        (
            _build_install_cmd(no_binary=["<format_control1>", "<format_control2>"]),
            "--no-binary <format_control1> --no-binary <format_control2>",
        ),
        (_build_install_cmd(build_isolation=False), "--no-build-isolation"),
        (_build_install_cmd(cache_dir=False), "--no-cache-dir"),
        (_build_install_cmd(clean=False), "--no-clean"),
        (_build_install_cmd(color=False), "--no-color"),
        (_build_install_cmd(compile=False), "--no-compile"),
        (_build_install_cmd(deps=False), "--no-deps"),
        (_build_install_cmd(index=False), "--no-index"),
        (_build_install_cmd(input=False), "--no-input"),
        (
            _build_install_cmd(python_version_warning=False),
            "--no-python-version-warning",
        ),
        (_build_install_cmd(warn_conflicts=False), "--no-warn-conflicts"),
        (_build_install_cmd(warn_script_location=False), "--no-warn-script-location"),
        (
            _build_install_cmd(only_binary="<format_control>"),
            "--only-binary <format_control>",
        ),
        (
            _build_install_cmd(only_binary=["<format_control1>", "<format_control2>"]),
            "--only-binary <format_control1> --only-binary <format_control2>",
        ),
        (_build_install_cmd(platform="<platform>"), "--platform <platform>"),
        (
            _build_install_cmd(platform=["<platform1>", "<platform2>"]),
            "--platform <platform1> --platform <platform2>",
        ),
        (_build_install_cmd(pre=True), "--pre"),
        (_build_install_cmd(prefer_binary=True), "--prefer-binary"),
        (_build_install_cmd(prefix="<dir>"), "--prefix <dir>"),
        (
            _build_install_cmd(progress_bar="<progress_bar>"),
            "--progress-bar <progress_bar>",
        ),
        (_build_install_cmd(proxy="<proxy>"), "--proxy <proxy>"),
        (_build_install_cmd(python="<python>"), "--python <python>"),
        (
            _build_install_cmd(python_version="<python_version>"),
            "--python-version <python_version>",
        ),
        (_build_install_cmd(q=True), "-q"),
        (_build_install_cmd(q=1), "-q"),
        (_build_install_cmd(q=2), "-qq"),
        (_build_install_cmd(q=3), "-qqq"),
        (_build_install_cmd(quiet=True), "--quiet"),
        (_build_install_cmd(r="<file>"), "-r <file>"),
        (_build_install_cmd(r=["<file1>", "<file2>"]), "-r <file1> -r <file2>"),
        (_build_install_cmd(report="<file>"), "--report <file>"),
        (_build_install_cmd(require_hashes=True), "--require-hashes"),
        (_build_install_cmd(require_virtualenv=True), "--require-virtualenv"),
        (_build_install_cmd(requirement="<file>"), "--requirement <file>"),
        (
            _build_install_cmd(requirement=["<file1>", "<file2>"]),
            "--requirement <file1> --requirement <file2>",
        ),
        (_build_install_cmd(retries="<retries>"), "--retries <retries>"),
        (_build_install_cmd(root="<dir>"), "--root <dir>"),
        (
            _build_install_cmd(root_user_action="<root_user_action>"),
            "--root-user-action <root_user_action>",
        ),
        (_build_install_cmd(src="<dir>"), "--src <dir>"),
        (_build_install_cmd(t="<dir>"), "-t <dir>"),
        (_build_install_cmd(target="<dir>"), "--target <dir>"),
        (_build_install_cmd(timeout="<sec>"), "--timeout <sec>"),
        (_build_install_cmd(trusted_host="<hostname>"), "--trusted-host <hostname>"),
        (_build_install_cmd(U=True), "-U"),
        (_build_install_cmd(upgrade=True), "--upgrade"),
        (
            _build_install_cmd(upgrade_strategy="<upgrade_strategy>"),
            "--upgrade-strategy <upgrade_strategy>",
        ),
        (_build_install_cmd(use_deprecated="<feature>"), "--use-deprecated <feature>"),
        (_build_install_cmd(use_feature="<feature>"), "--use-feature <feature>"),
        (_build_install_cmd(use_pep517=True), "--use-pep517"),
        (_build_install_cmd(user=True), "--user"),
        (_build_install_cmd(V=True), "-V"),
        (_build_install_cmd(v=True), "-v"),
        (_build_install_cmd(v=1), "-v"),
        (_build_install_cmd(v=2), "-vv"),
        (_build_install_cmd(v=3), "-vvv"),
        (_build_install_cmd(verbose=True), "--verbose"),
        (_build_install_cmd(version=True), "--version"),
    ]
    for output, expected in man_page_args:
        assert " ".join(output[2:]) == expected


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
