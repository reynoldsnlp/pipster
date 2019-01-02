from glob import glob
import os
from pprint import pprint
import shlex
import six
from subprocess import PIPE
from subprocess import run
import sys
from warnings import warn

try:
    from pip._internal.commands import InstallCommand
    install_cmd = InstallCommand()
except ModuleNotFoundError:
    raise ModuleNotFoundError('Please install pip for the current '
                              'interpreter: (%s).' % sys.executable)

pipfiles = []
for i in range(4):  # 4 is completely arbitrary here
    pipfiles.extend(glob(('..' + os.sep) * i + 'Pipfile'))
if pipfiles:
    pipfiles = [os.path.abspath(f) for f in pipfiles]
    msg = ('Warning: the following Pipfiles will be bypassed by '
           'pip_inside.install:\n\t' + '\n\t'.join(pipfiles))
    warn(msg, stacklevel=2)


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
        # Keyword arguments are translated to CLI options
        for raw_k, v in kwargs.items():
            k = raw_k.replace('_', '-') # Translate Python identifiers to CLI long option names
            append_value = isinstance(v, six.string_types)
            if append_value
                # When the arg value is a string, both it and the option are appended to the CLI args
                append_option=True
                if not v:
                    raise ValueError("Empty string passed as value for option {}".format(k))
            else:
                # Otherwise we assume the value indicates whether or not to include a boolean flag and
                # handle it as a tri-state setting (None->omit, true->include, false->include negated)
                append_option = v is not None
                if k.startswith("no-"):
                    # Instead of accepting both `some-option=True` and `no-some-option=False`, we
                    # disallow the second spelling, but suggest the former when the latter is tried
                    raw_suffix = raw_k[3:]
                    msg_template = "Rather than '{}={!r}', try '{{}}={{!r}}'".format(raw_k, v)
                    if append_option:
                        translation_suggestion = msg_template.format(raw_suffix, not v)
                    else:
                        translation_suggestion = msg_template.format(raw_suffix, None)
                    raise ValueError(translation_suggestion)                   
                if append_option and not v:
                    k = "no-" + k
            if append_option:
                if len(k) == 1:  # short flag
                    option = "-" + k
                else:  # long flag
                    option = "--" + k
                cli_args.append(option)
                if append_value:
                    cli_args.append(v)
        # Positional arguments are passed directly as CLI arguments
        cli_args += args
    # use pip internals to isolate package names
    opt_dict, targets = install_cmd.parse_args(cli_args)
    assert targets[:2] == ['pip', 'install']
    targets = set(targets[2:])
    already_loaded = {n: mod for n, mod in sys.modules.items() if n in targets}
    print('Trying  ', ' '.join(cli_args), '  ...')
    result = run([sys.executable, "-m", *cli_args], stdout=PIPE, stderr=PIPE)
    print(result)

    if result.returncode == 0 and already_loaded:
        print('The following modules were already loaded. You may need to '
              'restart python to see changes: ')
        pprint(already_loaded)
