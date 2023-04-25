import subprocess
import sys

try:
    from pip._internal.commands.install import InstallCommand
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        f"Please install pip for the current interpreter: {sys.executable}"
    )

from .utils import pip_help_with_python_kwargs
from .utils import check_for_pipfiles
from .utils import build_cmd
from .utils import get_requirements_from_file
from .utils import check_if_already_loaded

__all__ = ["install"]
install_cmd = InstallCommand(name="Install", summary="Provides parse_args.")


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


install.__doc__ += pip_help_with_python_kwargs("install", install_cmd)


def _install(*args, **kwargs) -> subprocess.CompletedProcess:
    """Allows install() to hide CompletedProcess in REPL output."""
    check_for_pipfiles()
    cli_args = build_cmd("install", *args, **kwargs)
    # use pip internals to isolate package names
    req_args, req_targets = install_cmd.parse_args(cli_args)
    if req_args.requirements:  # -r requirements.txt
        reqs_from_file = get_requirements_from_file(req_args.requirements)
        req_targets.extend(reqs_from_file)
    assert req_targets[:2] == ["pip", "install"]
    already_loaded = check_if_already_loaded(req_targets[2:])
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
