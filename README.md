# pipster

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
