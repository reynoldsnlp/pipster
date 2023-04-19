from pipster.install import _pip_install_help_with_python_kwargs


def test__pip_install_help_with_python_kwargs():
    """This test will break anytime pip's optparse options are changed.
    The point is to manually check that the automatic conversion to
    kwargs is working and then update the file.

    Generate the new file using the following code:

    python3 -c "from pipster.install import _pip_install_help_with_python_kwargs;
            print(_pip_install_help_with_python_kwargs())" \
            > tests/data/pip_install_help_with_python_kwargs.txt
    """
    with open("tests/data/pip_install_help_with_python_kwargs.txt") as f:
        assert _pip_install_help_with_python_kwargs().strip() == f.read().strip()
