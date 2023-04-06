# pipster

<div align="center">
    <img src="https://raw.githubusercontent.com/reynoldsnlp/pipster/main/images/pipster_138x250.jpg" alt="Pipster logo" width="138">
<br/>
<br/>

| | |
| --- | --- |
| CI/CD | [![CI - Test and Build](https://github.com/reynoldsnlp/pipster/actions/workflows/test_build_publish.yml/badge.svg)](https://github.com/reynoldsnlp/pipster/actions/workflows/test_build_publish.yml) |
| Package | [![PyPI - Version](https://img.shields.io/pypi/v/pipster.svg?logo=pypi&label=PyPI&logoColor=gold)](https://pypi.org/project/pipster/) [![PyPI - Downloads](https://img.shields.io/pypi/dm/pipster.svg?color=blue&label=Downloads&logo=pypi&logoColor=gold)](https://pypi.org/project/pipster/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pipster.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/pipster/) |
| Meta | [![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://github.com/charliermarsh/ruff) [![code style - Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy) [![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/) [![GitHub Sponsors](https://img.shields.io/github/sponsors/reynoldsnlp?logo=GitHub%20Sponsors&style=social)](https://github.com/sponsors/reynoldsnlp) |

</div>

## Intro

Install packages using `pip` from inside a python script or console:

```python
>>> from pipster import install
>>> install("some_package")
```

This tool solves the age-old problem of `pip install`ing a package only to find
that you still can't import it because it was installed for the wrong
interpreter. By installing from inside python, you ensure that it will be
available to import from that instance of python.

If you re-install, upgrade, or downgrade a package _after_ it has already been
imported, `pipster` will do its best to detect this and issue a warning that
Python should be restarted for changes to be available.

```python
>>> from pipster import install
>>> import requests
>>> requests.__version__
'2.27.0'
>>> install("requests", upgrade=True)
...
Successfully installed requests-2.28.2

WARNING: The following modules were already loaded. Restart python to see changes:
requests
```

**Note:** The developers of `pipster` hope that this tool will eventually be
integrated into `pip` so that every Python installation has this capability.
The maintainers of `pip` have [expressed
interest](https://github.com/pypa/pip/issues/5069) in making this happen, but
first `pipster` needs to be extensively tested and used in real life. By
sharing this tool with others, and reporting bugs/issues if they arise, you are
helping us achieve that goal.

## Installation

To install `pipster`, run the following in your terminal (you may need to
replace `python` with the name of the executable you use to run Python, such as
`python3`, `python3.11`, etc.):

```
$ python -m pip install --user pipster
```

...and if that's not working, you can run this in a python script or console:

```python
import subprocess
import sys
cmd = [sys.executable,  "-m", "pip", "install", "--user", "pipster"]
subprocess.check_call(cmd)
```

## Usage

The `install()` function can be called in two ways.

### Copy-paste `pip install ...`

If you give `install()` a single string that begins with `pip install`, then it
will run that exact command as if it were given at the command line.

```python
install("pip install some_package")`
install("pip install --user --upgrade pkg1 pkg2 pkg3")
```

### Python function API

You can also pass any number of target packages along with keyword arguments
corresponding to commandline options for `pip install`. Note that the python
keyword arguments use `_` instead of `-`.

The `pipster.install()` function does not validate which options are available
in the commandline. If you give it arguments that are not valid commandline
options, then it will attempt to run `pip install` with those options, and
`pip` will return an error.

#### Boolean options

Most boolean commandline options are set by giving `<option>=True`.

```python
install("pkg", user=True)     # pip install --user pkg
install("pkg", upgrade=True)  # pip install --upgrade pkg
```

Boolean commandline options that begin with `--no-`, such as `--no-color` are
set by removing the `no-` prefix and using `<option>=False`.

```python
install("pkg", color=False)  # pip install --no-color pkg
install("pkg", deps=False)   # pip install --no-deps pkg
```

#### Key-value options

Usually, key-value options are set using a string: `<option>="<value>"`.

```python
install(r="requirements.txt")         # pip install -r requirements.txt
install("pkg", python_version="3.8")  # pip install --python-version 3.8 pkg
```

However, some key-value options can be used multiple times. In these cases,
the value given should be a list of strings: `<option>=["<val1>", "<val2>"]`.

```python
install(r=["reqs1.txt", "reqs2.txt"])  # pip install -r reqs1.txt -r reqs2.txt
```

#### Additive options

Some commandline options are additive (notably `-q` and `-v`), and can be used
up to 3 times. These can be set using either an integer or `True`.

```python
install('pkg', v=True)  # pip install -v pkg
install('pkg', v=1)     # pip install -v pkg
install('pkg', v=2)     # pip install -vv pkg
install('pkg', v=3)     # pip install -vvv pkg
```

#### Omitting options

Any option that is assigned the value `None` is omitted from the command. This
feature facilitates simpler logic in preparing keyword arguments
programmatically.

```python
user = None
if <logical test>:
  user = True
install('pkg', user=user)
```

## Pipfiles

Pipfiles are ignored by `pipster`. If you use `pipster` from a directory that
contains a Pipfile (or whose parent directories up to a depth of 3 contain a
Pipfile), then `pipster` will issue a warning that Pipfiles are ignored.
