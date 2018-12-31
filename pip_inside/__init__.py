from pprint import pprint
import re
import shlex
from subprocess import PIPE
from subprocess import run
import sys

try:
    from pip._internal.commands import InstallCommand
    install_cmd = InstallCommand()
except ModuleNotFoundError:
    raise ModuleNotFoundError('Please install pip for the current '
                              'interpreter: (%s).' % sys.executable)

# TODO(RJR) https://github.com/pypa/pip/issues/5069#issue-305765776
# if Pipfile or Pipfile.lock is seen, emit a warning to stderr about it being bypassed (such a
# warning could potentially be added to pip by default regardless of how it's invoked)


def install(*args, **kwargs):
    """Install packages into the current environment.

    Equivalent examples of command-line pip and pip_inside are grouped below.

    METHOD 1: Single argument is exactly the same as command line interface,
    beginning with 'pip install ...'

    $ pip install --user --upgrade some_pkg
    >>> install('pip install --user --upgrade some_pkg')

    METHOD 2: Arguments from command-line implementation split on spaces

    $ pip install some_pkg
    >>> install('some_pkg')

    $ pip install --user --upgrade some_pkg
    >>> install('--user', '--upgrade', 'some_pkg')
    >>> install(*'--user --upgrade some_pkg'.split())

    If preferred, keyword-value arguments can also be used:

    $ pip install -r requirements.txt
    >>> install(r='requirements.txt')
    >>> install('-r', 'requirements.txt')
    >>> install(*'-r requirements.txt'.split())

    $ pip install --no-index --find-links=/local/dir/ some_pkg
    # Note the use of '_' in the following keyword example.
    >>> install('--no-index', 'some_pkg', find_links='/local/dir/')
    >>> install('--no-index', '--find-links=/local/dir/', 'some_pkg')
    >>> install(*'--no-index --find-links=/local/dir/ some_pkg'.split())

    """
    if len(args) == 1 and args[0].startswith('pip install '):
        cli_args = shlex.split(args[0])
    else:
        cli_args = ['pip', 'install']
        # TODO(RJR) https://github.com/pypa/pip/issues/5069#issuecomment-450605456
        # add keyw
        for k, v in kwargs.items():
            if len(k) == 1:  # short flag
                cli_args.append("-" + k)
                if v is not True:  # True signals that the flag is just a boolean
                    cli_args.append(v)
            else:  # long flag
                cli_args.append("--" + k.replace('_', '-'))
                if v is not True:  # True signals that the flag is just a boolean
                    cli_args.append(v)
        cli_args += args
    # use pip internals to isolate package names
    opt_dict, target_names = install_cmd.parse_args(cli_args)
    assert target_names[:2] == ['pip', 'install']
    target_names = set(target_names[2:])

# TODO(RJR) redo already_loaded using __spec__.origin ??
# https://github.com/pypa/pip/issues/5069#issue-305765776
# after the installation operation completes, read the RECORD entries for any just installed
# modules, and compare them to __spec__.origin and
# importlib.util.source_from_cache(__spec__.origin__) for all of the modules in sys.modules.values()
# and emit a warning to stderr suggesting a Python session restart if any of the just installed
# files is already loaded in the module cache

    already_loaded = {name: module for name, module in sys.modules.items() if name in target_names}
    print('Trying  ', ' '.join(cli_args), '  ...', '(', ', '.join(target_names), ')')
    result = run([sys.executable, "-m", *cli_args], stdout=PIPE, stderr=PIPE)
    print(result)

    if result.returncode == 0 and already_loaded:
        print('The following modules were already loaded. You may need to restart python to see '
              'changes: ')
        pprint(already_loaded)
