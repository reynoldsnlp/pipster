import ast
import inspect
import os
import re
import subprocess
import sys

from .. import install

__all__ = ["autoinstall"]


def _get_stdlib_module_names():
    if sys.version_info >= (3, 10):
        return sys.stdlib_module_names
    else:
        # The following import causes warnings in python >= 3.10
        import distutils.sysconfig as sysconfig

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
    stdlib_module_names = _get_stdlib_module_names()
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
            if "import" in line and re.search(r"#\s*(?:skip\s+)?install\s+", line)
        ]
    skips = {
        dep
        for dep in deps
        for line in install_lines
        if f" {dep}" in line and re.search(r"#\s*skip\s+install", line)
    }
    dep_pkg_list = []
    for dep in deps:
        if dep in skips:
            continue
        pkgs = [
            m.group(1).split()
            for line in install_lines
            if f" {dep}" in line
            and (m := re.search(r"#\s+install\s+([\s0-9A-Za-z-_.]+)", line))
        ]
        pkgs = set(pkg for group in pkgs for pkg in group if pkg)  # flatten pkgs
        dep_pkg_list.append((dep, tuple(pkgs) or None))
    return dep_pkg_list


def _is_installed(pkg):
    """Check whether pkg is already installed."""
    result = subprocess.run([sys.executable, "-m", "pip", "show", pkg])
    return not result.returncode


def autoinstall(interactive=True, **kwargs):
    """Install all packages imported in the module where this function is
    called.  Packages already installed will be skipped unless upgrade=True.

    If the package/distribution name to be installed is different from the
    module name (e.g. scikit-learn vs sklearn), the package name(s) should be
    provided in an in-line comment beginning with install:
    `import sklearn  # install scikit-learn`. To ignore an import, add an
    in-line comment beginning with `# skip install`.

    Other than `interactive`, all keyword arguments are passed to pip, e.g.
    `autoinstall(user=True, upgrade=True, index_url='https://example.com')`.

    This function does not look for transitive dependencies. Only import
    statements in the module where this function is called are considered.
    """
    try:
        upgrade = kwargs["upgrade"]
    except KeyError:
        upgrade = False

    filename = inspect.stack()[1].filename
    deps = _get_deps(filename)
    if not interactive:
        targets = []
        for mod, pkgs in deps:
            if pkgs:
                targets.extend(pkgs)
            else:
                targets.append(mod)
        if not upgrade:
            orig_targets, targets, installed_tgts = targets, [], []
            for t in orig_targets:
                if _is_installed(t):
                    installed_tgts.append(t)
                else:
                    targets.append(t)
            print(f'{" ".join(installed_tgts)} already installed.', file=sys.stderr)
        print(f'autoinstall is installing {" ".join(targets)} ...', file=sys.stderr)
        install(*deps, **kwargs)
    else:
        for mod, pkgs in deps:
            if pkgs:
                targets = pkgs
            else:
                targets = [mod]

            if not upgrade and all(_is_installed(pkg) for pkg in targets):
                print(f"{' '.join(targets)} already installed.", file=sys.stderr)
                continue

            while True:
                resp = input(
                    f"Install {' '.join(targets)}? (Y)es / (N)o / (C)ustomize name  "
                )  # noqa: E501
                if re.search(r"y(?:es)?", resp, flags=re.I):
                    print(f"Installing {' '.join(targets)}...", file=sys.stderr)
                    install(*targets, **kwargs)
                    break
                elif re.search(r"no?", resp, flags=re.I):
                    break
                elif re.search(r"c(?:ustom)?", resp, flags=re.I):
                    pkg_name = input(
                        f"What package(s) would you like to install instead of {' '.join(targets)}? "  # noqa: E501
                    )
                    print(f"Installing {pkg_name}...", file=sys.stderr)
                    install(*pkg_name.split(), **kwargs)
                    break
                else:
                    print(
                        'Invalid input. Type "y", "n", or "c" and press [enter].',
                        file=sys.stderr,
                    )
