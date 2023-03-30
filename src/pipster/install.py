from glob import glob
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
from warnings import warn

try:
    from pip._internal.commands.install import InstallCommand
    from pip._vendor.distlib.database import DistributionPath
    install_cmd = InstallCommand(name='dummy', summary='Provides parse_args.')
except ModuleNotFoundError:
    raise ModuleNotFoundError('Please install pip for the current '
                              'interpreter: (%s).' % sys.executable)

__all__ = ['install']


pipfiles = []
for i in range(4):  # TODO: 4 is completely arbitrary here. improve?
    pipfiles.extend(glob(('..' + os.sep) * i + 'Pipfile'))
if pipfiles:
    pipfiles = [os.path.abspath(f) for f in pipfiles]
    msg = ('Warning: the following Pipfiles will be bypassed by '
           'pipster.install:\n\t' + '\n\t'.join(pipfiles))
    warn(msg, stacklevel=2)


def _parse_target(target):
    """Parse install target down to the distribution name."""
    # TODO: make more robust
    if target.endswith('.whl'):
        return Path(target).name.split('-')[0]
    else:
        # https://pip.pypa.io/en/stable/reference/requirement-specifiers/
        return re.search(r'(.+?)(?:[!~<>=]{1,2}.+)?$', target).group(1)


def install(*args, **kwargs):
    """Install packages into the current environment.

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
    >>> install(*'--user --upgrade some_pkg'.split())

    If preferred, keyword-value arguments can also be used:

    $ pip install -r requirements.txt
    >>> install(r='requirements.txt')
    >>> install('-r', 'requirements.txt')
    >>> install(*'-r requirements.txt'.split())

    $ pip install --no-index --find-links /local/dir/ some_pkg
    # Note the use of '_' in the following keyword example.
    >>> install('--no-index', 'some_pkg', find_links='/local/dir/')
    >>> install('--no-index', '--find-links', '/local/dir/', 'some_pkg')
    >>> install(*'--no-index --find-links /local/dir/ some_pkg'.split())

    """
    cli_args = _build_install_cmd(*args, **kwargs)
    # use pip internals to isolate package names
    _, req_targets = install_cmd.parse_args(cli_args)
    assert req_targets[:2] == ['pip', 'install']
    req_targets = [_parse_target(t) for t in req_targets[2:]]
    dist_path = DistributionPath(include_egg=True)
    target_providers = [d.modules
                        for t in req_targets
                        for d in dist_path.get_distributions()  # installed
                        if t == d.name]
    target_providers = [y for x in target_providers for y in x]  # flatten
    target_origins = {}
    for t in target_providers:
        if t in sys.modules:
            target_origins[sys.modules[t].__spec__.origin] = t
    dist_path = DistributionPath(include_egg=True)
    dists = [dist_path.get_distribution(t) for t in req_targets]
    paths = set()
    for dist in dists:
        if dist is not None:
            for path, _, _ in dist.list_installed_files():
                paths.add(os.path.join(os.path.dirname(dist.path), path))
    already_loaded = paths.intersection(target_origins)
    already_loaded = [target_origins[origin] for origin in already_loaded]
    print('Trying  ', ' '.join(cli_args), '  ...', file=sys.stderr)
    cli_cmd = [sys.executable, "-m"] + cli_args
    result = subprocess.run(cli_cmd, check=True)
    if result.returncode == 0 and already_loaded:
        warn('WARNING! The following modules were already loaded. Restart '
             f'python to see changes:  {", ".join(already_loaded)}',
             UserWarning)
    return result


def _build_install_cmd(*args, **kwargs):
    if len(args) == 1 and args[0].startswith('pip install '):
        return shlex.split(args[0])
    else:
        cli_args = ['pip', 'install']
        # Keyword arguments are translated to CLI options
        for raw_k, v in kwargs.items():
            k = raw_k.replace('_', '-')  # Python identifiers -> CLI long names
            append_value = isinstance(v, str)
            if append_value:
                # When arg value is str, append both it and option to CLI args
                append_option = True
                if not v:
                    raise ValueError("Empty string passed as value for option "
                                     "{}".format(k))
            else:
                # assume the value indicates whether to include a boolean flag.
                # None->omit, true->include, false->include negated
                append_option = v is not None
                if k.startswith("no-"):
                    # suggest `some-option=True` instead of
                    # `no-some-option=False`
                    raw_suffix = raw_k[3:]
                    msg_template = ("Rather than '{}={!r}', "
                                    "try '{{}}={{!r}}'".format(raw_k, v))
                    if append_option:
                        suggestion = msg_template.format(raw_suffix, not v)
                    else:
                        suggestion = msg_template.format(raw_suffix, None)
                    raise ValueError(suggestion)
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
    return cli_args
