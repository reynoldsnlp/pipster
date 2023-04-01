import ast
import distutils.sysconfig as sysconfig
import inspect
import os
import re
import sys

from . import install

__all__ = ["autoinstall"]


def get_stdlib_module_names():
    if sys.version_info >= (3, 10):
        return sys.stdlib_module_names
    else:
        stdlib_module_names = set()
        std_lib = sysconfig.get_python_lib(standard_lib=True)

        for top, dirs, files in os.walk(std_lib):
            for nm in files:
                prefix = top[len(std_lib) + 1 :]
                if prefix[:13] == "site-packages":
                    continue
                if nm == "__init__.py":
                    stdlib_module_names.add(
                        top[len(std_lib) + 1 :].replace(os.path.sep, ".")
                    )
                elif nm[-3:] == ".py":
                    stdlib_module_names.add(
                        os.path.join(prefix, nm)[:-3].replace(os.path.sep, ".")
                    )
                elif nm[-3:] == ".so" and top[-11:] == "lib-dynload":
                    stdlib_module_names.add(nm[0:-3])
        for builtin in sys.builtin_module_names:
            stdlib_module_names.add(builtin)
        return stdlib_module_names


def _get_deps(path, include_stdlib=False):
    stdlib_module_names = get_stdlib_module_names()
    with open(path) as f:
        root = ast.parse(f.read(), path)

    deps = []
    for node in ast.walk(root):
        if isinstance(node, ast.Import):
            for n in node.names:
                mod = n.name.split(".")[0]
                if include_stdlib or mod not in stdlib_module_names:
                    deps.append(mod)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module.split(".")[0]
            if include_stdlib or mod not in stdlib_module_names:
                deps.append(mod)
        else:
            continue

    # allow comments to specify package name, e.g....
    # import sklearn  # install scikit-learn
    # TODO Make this robust a la https://stackoverflow.com/a/36055400/2903532
    with open(path) as f:
        install_lines = [
            line
            for line in f
            if "import" in line and re.search(r"#\s+install\s+", line)
        ]
    dep_pkg_list = []
    for dep in deps:
        pkgs = [
            m.group(1).split()
            for line in install_lines
            if dep in line
            and (m := re.search(r"#\s+install\s+([\s0-9A-Za-z-_.]+)", line))
        ]
        pkgs = set(pkg for group in pkgs for pkg in group if pkg)  # flatten pkgs
        dep_pkg_list.append((dep, tuple(pkgs) or None))
    return dep_pkg_list


def autoinstall(interactive=True, upgrade=False):
    filename = inspect.stack()[1].filename
    deps = _get_deps(filename)

    if not interactive:
        print(f'autoinstall is installing the following: {" ".join(deps)} ...')
        install(*deps, upgrade=upgrade)
    else:
        for mod, pkgs in deps:
            # TODO: check if dependency is installed
            print(f"{mod} is not installed.")
            while True:
                resp = input(f"Install {mod}? (Y)es / (N)o / (C)ustomize name  ")
                if re.search(r"y(?:es)?", resp, flags=re.I):
                    print(f"Installing {mod}...", file=sys.stderr)
                    install(mod, upgrade=upgrade)
                    break
                elif re.search(r"no?", resp, flags=re.I):
                    print("Okay. Taking no action.")
                    break
                elif re.search(r"c(?:ustom)?", resp, flags=re.I):
                    pkg_name = input(
                        f"What package would you like to install instead of {mod}? "
                    )
                    print(f"Installing {pkg_name}...", file=sys.stderr)
                    install(pkg_name, upgrade=upgrade)
                    break
                else:
                    print('Invalid input. Type "y", "n", or "c" and press [enter].')
