# pip\_inside

Install packages using `pip` from inside a python console/interpreter:

```python
>>> from pip_inside import install
>>> install('pip install useful_module')
```

This tool solves the age-old problem of `pip install`ing a package only to
realize that it was installed for the wrong interpreter. By installing from the
interpreter, such mismatches are unlikely to occur.

## Installation

Until the first release on PYPI, the following method will install `pip_inside`
from the python console/REPL:
```python
import subprocess
import sys
cmd = 'pip install --user git+https://github.com/reynoldsnlp/pip_inside'
cmd = [sys.executable,  '-m'] + cmd.split()
subprocess.check_call(cmd)

... or from `bash`:

```bash
$ pip install --user git+https://github.com/reynoldsnlp/pip_inside
```
