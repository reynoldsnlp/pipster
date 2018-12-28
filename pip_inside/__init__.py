import subprocess
from sys import executable

try:
    import pip
except ModuleNotFoundError:
    raise ModuleNotFoundError('Please install pip for the current '
                              'interpreter: (%s).' % executable)


def install(*args, **kwds):
    """Install packages into the current environment.

    Equivalent examples of pip_inside and command line pip are grouped below.

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

    $ pip install -r requirements.txt
    >>> install('-r', 'requirements.txt')
    >>> install(*'-r requirements.txt'.split())

    If preferred, keyword-value arguments can also be used:

    $ pip install --no-index --find-links=/local/dir/ some_pkg
    >>> install('--no-index', '--find-links=/local/dir/', 'some_pkg')
    >>> install(*'--no-index --find-links=/local/dir/ some_pkg'.split())
    >>> install('--no-index', 'some_pkg', find-links='/local/dir/')

    """
    if len(args) == 1 and args[0].startswith('pip install '):
        cli_args = args[0].split()
    else:
        cli_args = ['pip', 'install']
        for k, v in kwds:
            if len(k) == 1:  # short flag
                cli_args.append("-" + k)
                cli_args.append(v)
            else:  # long flag
                cli_args.append("--" + k.replace('_', '-'))
                cli_args.append(v)
        cli_args += args
    print('Trying  ', ' '.join(cli_args), '  ...')
    return subprocess.run([executable, "-m", *cli_args])
