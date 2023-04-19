from glob import glob
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import List
from typing import Optional
from urllib.parse import urlparse
from warnings import warn

try:
    from pip._internal.commands.install import InstallCommand
    from pip._internal.network.session import PipSession
    from pip._internal.req.req_file import parse_requirements
    from pip._vendor.distlib.database import DistributionPath
    from pip._vendor.packaging.requirements import InvalidRequirement
    from pip._vendor.packaging.requirements import Requirement
    from pip._vendor.packaging.utils import InvalidSdistFilename
    from pip._vendor.packaging.utils import InvalidWheelFilename
    from pip._vendor.packaging.utils import parse_wheel_filename
    from pip._vendor.packaging.utils import parse_sdist_filename
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        f"Please install pip for the current interpreter: {sys.executable}"
    )

from ._formatter import PythonHelpFormatter


__all__ = ["install"]
install_cmd = InstallCommand(name="Install", summary="Provides parse_args.")


def _pip_install_help_with_python_kwargs():
    """Prepare 'appendix' to add to docstring of install()."""
    w = 72  # width
    msg1 = "THE FOLLOWING IS DYNAMICALLY ADAPTED FROM `pip install --help`,"
    msg2 = "SHOWING PYTHON KEYWORD ARGUMENTS INSTEAD OF COMMAND-LINE OPTIONS."
    msg = "\n".join(
        ["", "=" * w, "=" * w, f"{msg1:^{w}}", f"{msg2:^{w}}", "=" * w, "=" * w, "", ""]
    )

    help = install_cmd.parser.format_help(PythonHelpFormatter())
    # remove CLI Usage section
    help = re.sub(r"\s*Usage:.*?\n(?=Description:\n)", "", help, flags=re.S)

    return msg + help


def _check_for_pipfiles(depth=3):  # `3` taken from pipenv.utils.pipfile.find_pipfile()
    pipfiles = []
    for i in range(depth):
        pipfiles.extend(glob((".." + os.sep) * i + "Pipfile"))
    if pipfiles:
        pipfiles = [os.path.abspath(f) for f in pipfiles]
        msg = (
            "Warning: the following Pipfiles will be bypassed by "
            f"pipster.install: ({' '.join(pipfiles)})"
        )
        warn(msg, stacklevel=2)


def _check_if_already_loaded(requirements):
    req_targets = [_get_dist_name(r) for r in requirements]
    dist_path = DistributionPath(include_egg=True)
    target_providers = [
        d.modules
        for t in req_targets
        for d in dist_path.get_distributions()  # installed
        if t == d.name
    ]
    target_providers = [y for x in target_providers for y in x]  # flatten
    target_origins = {}
    for t in target_providers:
        if t in sys.modules:
            module_spec = sys.modules[t].__spec__
            if module_spec is not None:
                target_origins[module_spec.origin] = t
    dist_path = DistributionPath(include_egg=True)
    dists = [dist_path.get_distribution(t) for t in req_targets]
    paths = set()
    for dist in dists:
        if dist is not None:
            for path, _, _ in dist.list_installed_files():
                paths.add(os.path.join(os.path.dirname(dist.path), path))
    already_loaded = paths.intersection(target_origins)
    already_loaded = {target_origins[origin] for origin in already_loaded}
    return already_loaded


def _get_dist_name(target: str) -> Optional[str]:
    """Parse install target down to the distribution name."""
    warn_msg = (
        f"If {target} was already imported, python must be restarted "
        "to import the newly installed version."
    )

    # parse `pip install "asdf @ ..."`
    at_match = re.match(r"([A-Za-z0-9.-_]+)\s+@\s+(.+)", target)
    if at_match:
        at_name, target = at_match.groups()
    else:
        at_name = None

    if _is_valid_url(target):
        parsed_url = urlparse(target)
        if egg_match := re.search(r"egg=([A-Za-z0-9-_.]+)", parsed_url.fragment):
            return egg_match.group(1)
        elif re.search(r"\.(?:whl|tar\.gz|zip)$", parsed_url.path):
            filename = Path(parsed_url.path).name
            try:
                return _get_dist_name_from_filename(filename)
            except (InvalidSdistFilename, InvalidWheelFilename):
                return at_name
        else:
            if at_name:
                return at_name
            else:
                warn(warn_msg, UserWarning)
                return None  # TODO  Can this be determined further?
    elif re.search(r"\.(?:whl|tar\.gz|zip)$", target):
        filename = Path(target).name
        try:
            return _get_dist_name_from_filename(filename)
        except (InvalidSdistFilename, InvalidWheelFilename):
            return at_name
    else:
        try:
            return Requirement(target).name
        except InvalidRequirement:
            # Probably a directory. TODO use `os.path.isdir` and `setup.py egg_info`?
            if at_name:
                return at_name
            else:
                warn(warn_msg, UserWarning)
                return None


def _get_dist_name_from_filename(filename):
    if filename.endswith(".whl"):
        name, _, _, _ = parse_wheel_filename(filename)
        return name
    elif filename.endswith(".tar.gz") or filename.endswith(".zip"):
        name, _ = parse_sdist_filename(filename)
        return name
    else:
        raise ValueError(f"{filename} does not end in whl, tar.gz, or zip.")


def _is_valid_url(url):
    try:
        parsed_url = urlparse(url)
        return parsed_url.scheme and (
            parsed_url.netloc or parsed_url.scheme.endswith("file")
        )
    except:  # noqa: E722
        return False


def _get_requirements_from_file(filename):
    """Parse requirements.txt file into individual requirements."""
    return [r.requirement for r in parse_requirements(filename, PipSession())]


def install(*args, **kwargs) -> None:
    """
    Install packages into the current environment.

    Equivalent examples of command-line pip and pipster are grouped below.

    METHOD 1: Single argument is exactly the same as command line interface,
    beginning with 'pip install ...'

    $ pip install --user --upgrade some_pkg
    >>> install('pip install --user --upgrade some_pkg')

    METHOD 2: Arguments from command-line implementation split on spaces

    $ pip install some_pkg
    >>> install('some_pkg')

    $ pip install --user --upgrade some_pkg
    >>> install('--user', '--upgrade', 'some_pkg')
    >>> install('some_pkg', user=True, upgrade=True)

    If preferred, keyword-value arguments can also be used:

    $ pip install -r requirements.txt
    >>> install('-r', 'requirements.txt')
    >>> install(r='requirements.txt')

    $ pip install --no-index --find-links /local/dir/ some_pkg
    >>> install('--no-index', '--find-links', '/local/dir/', 'some_pkg')
    # Note the use of '_' in the following keyword example.
    >>> install('some_pkg', index=False, find_links='/local/dir/')
    """
    _ = _install(*args, **kwargs)


install.__doc__ += _pip_install_help_with_python_kwargs()


def _install(*args, **kwargs) -> subprocess.CompletedProcess:
    """Allows install() to hide CompletedProcess in REPL output."""
    _check_for_pipfiles()
    cli_args = _build_install_cmd(*args, **kwargs)
    # use pip internals to isolate package names
    req_args, req_targets = install_cmd.parse_args(cli_args)
    if req_args.requirements:  # -r requirements.txt
        reqs_from_file = _get_requirements_from_file(req_args.requirements)
        req_targets.extend(reqs_from_file)
    assert req_targets[:2] == ["pip", "install"]
    already_loaded = _check_if_already_loaded(req_targets[2:])
    print("Running `", " ".join(cli_args), "`  ...", file=sys.stderr)
    cli_cmd = [sys.executable, "-m"] + cli_args
    result = subprocess.run(cli_cmd, check=True)
    if result.returncode == 0 and already_loaded:
        print(
            "\n\033[0;31mWARNING:\033[00m The following modules were already loaded. "
            "Restart python to see changes:\n"
            f"\033[0;32m{'os.linesep'.join(already_loaded)}\033[00m\n"
        )
    return result


def _build_install_cmd(*args, **kwargs) -> List[str]:
    if len(args) == 1 and args[0].startswith("pip install "):
        return shlex.split(args[0])
    else:
        cli_args = ["pip", "install"]
        # Keyword arguments are translated to CLI options
        for raw_k, v in kwargs.items():
            k = raw_k.replace("_", "-")  # Python identifiers -> CLI long names
            if len(k) == 1:
                option = "-" + k
            else:
                option = "--" + k

            if v is None:
                # None->omit
                continue
            elif isinstance(v, bool):
                # true->include, false->include negated
                if k.startswith("no-"):
                    # suggest `some-option=True` instead of
                    # `no-some-option=False`
                    sugg_k = raw_k[3:]
                    raise ValueError(
                        f"Rather than '{raw_k}={v!r}', try '{sugg_k}={not v!r}'"
                    )
                if not v:
                    option = option.replace("--", "--no-")
                cli_args.append(option)
            elif isinstance(v, str):
                if not v:
                    raise ValueError(f"Empty string passed as value: ({raw_k}={v!r}")
                cli_args.extend([option, v])
            # Handle additive args (indicated by int value, e.g. q=3 -> -qqq)
            elif isinstance(v, int):  # v=1 (i.e. v=True) already handled above
                if len(k) == 1:
                    cli_args.append(f"-{k * v}")
                else:
                    cli_args.extend([option] * v)
                continue
            # Handle repeatable key-value arguments
            elif isinstance(v, list) or isinstance(v, tuple):
                if not all(isinstance(s, str) for s in v):
                    raise ValueError(
                        f"Not all elements of list/tuple are strings ({raw_k}={v!r})"
                    )
                for each_val in v:
                    cli_args.extend([option, each_val])
            else:
                raise ValueError(
                    "Value must be of type bool/str/int/list/tuple/None, "
                    f"not {type(v)} (from {raw_k}={v!r})"
                )
        # Positional arguments are passed directly as CLI arguments
        cli_args += args
    return cli_args
