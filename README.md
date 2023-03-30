# pipster  🐍 🧔‍♂️ 🚲 🍺

> &#8220;I was `pip install`ing from the script or console before it was cool&#8221;

<div>
  <img src="" alt="Pipster logo" width="138" role="img" style="float: left; margin: 0 15px 0 0">

| | |
| --- | --- |
| CI/CD | [![CI - Test and Build](https://github.com/reynoldsnlp/pipster/actions/workflows/test_build_publish.yml/badge.svg)](https://github.com/reynoldsnlp/pipster/actions/workflows/test_build_publish.yml) |
| Package | [![PyPI - Version](https://img.shields.io/pypi/v/pipster.svg?logo=pypi&label=PyPI&logoColor=gold)](https://pypi.org/project/pipster/) [![PyPI - Downloads](https://img.shields.io/pypi/dm/pipster.svg?color=blue&label=Downloads&logo=pypi&logoColor=gold)](https://pypi.org/project/pipster/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pipster.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/pipster/) |
| Meta | [![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://github.com/charliermarsh/ruff) [![code style - Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy) [![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/) [![GitHub Sponsors](https://img.shields.io/github/sponsors/reynoldsnlp?logo=GitHub%20Sponsors&style=social)](https://github.com/sponsors/reynoldsnlp) |
</div>

Install packages using `pip` from inside a python script or console:

```python
>>> from pipster import install
>>> install('useful_package')
```

This tool solves the age-old problem of `pip install`ing a package only to find
that you still can't import it because it was installed for the wrong
interpreter. By installing from inside python, you ensure that it will be
available to import from that version python.

## Installation

Run the following in your terminal.

```
$ pip install --user pipster
```

...and if that's not working, you can run this in a python script or console:

```python
import subprocess
import sys
cmd = [sys.executable,  '-m', 'pip', 'install', '--user', 'pipster']
subprocess.check_call(cmd)
```
