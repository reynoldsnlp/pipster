# pip-inside

Install packages using `pip` from inside a python console/interpreter:

```python
>>> from pip_inside import install
>>> install(useful_module)
```

This tool solves the age-old problem of `pip install`ing a package only to
realize that it was installed for the wrong interpreter. By installing from the
interpreter, such mismatches are unlikely to occur.
