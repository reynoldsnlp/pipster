import ast
from collections import namedtuple
import inspect
from modulefinder import ModuleFinder
import re
import sys

from bs4 import BeautifulSoup as bs  # install beautifulsoup4
import libcst as cst
from sklearn.ensemble import RandomForestClassifier  # install scikit-learn
import requests as r
import numpy, pandas

from . import install
__all__ = ['autoinstall']


def _get_deps(path, include_stdlib=False):
    # TODO: sys.stdlib_module_names is only available in Python 3.10+
    with open(path) as f:
        root = ast.parse(f.read(), path)

    deps = []
    for node in ast.walk(root):
        if isinstance(node, ast.Import):
            for n in node.names:
                mod = n.name.split('.')[0]
                if include_stdlib or mod not in sys.stdlib_module_names:
                    deps.append(mod)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module.split('.')[0]
            if include_stdlib or mod not in sys.stdlib_module_names:
                deps.append(mod)
        else:
            continue

    # allow comments to specify package name, e.g....
    # import sklearn  # install scikit-learn
    # TODO Make this robust a la https://stackoverflow.com/a/36055400/2903532
    with open(path) as f:
        install_lines = [line for line in f
                         if 'import' in line
                         and re.search(r'#\s+install\s+', line)]
    dep_pkg_list = []
    for dep in deps:
        pkgs = [match.group(1).split()
                for line in install_lines
                if dep in line
                and (match := re.search(r'#\s+install\s+(.+)$', line))]
        pkgs = set(pkg for group in pkgs for pkg in group)  # flattened
        dep_pkg_list.append((dep, tuple(pkgs) or None))
    return dep_pkg_list


def autoinstall(interactive=True, upgrade=False):
    filename = inspect.stack()[1].filename
    deps = _get_deps(filename)

    if not interactive:
        print(f'autoinstall is installing the following: {" ".join(deps)} ...')
        # pip_inside.install(*deps, upgrade=upgrade)
    else:
        for mod, pkgs in deps:
            # TODO: check if dependency is installed
            print(f'{dep} is not installed.')
            while True:
                resp = input(f'Install {dep}? (Y)es / (N)o / (C)ustomize name  ')
                if re.search(r'y(?:es)?', resp, flags=re.I):
                    print(f'Installing {dep}...', file=sys.stderr)
                    # pip_inside.install(dep, upgrade=upgrade)
                    break
                elif re.search(r'no?', resp, flags=re.I):
                    print('Okay. Taking no action.')
                    break
                elif re.search(r'c(?:ustom)?', resp, flags=re.I):
                    pkg_name = input(f'What package name would you like to install instead of {dep}? ')
                    print(f'Installing {install_name}...', file=sys.stderr)
                    # pip_inside.install(pkg_name, upgrade=upgrade)
                    break
                else:
                    print('Invalid input. Type "y", "n", or "c" and press [enter].')
