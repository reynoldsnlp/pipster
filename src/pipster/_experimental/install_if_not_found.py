from contextlib import AbstractContextManager
import re
import sys


# TODO Compare this thing: https://github.com/mdipierro/autoinstaller/blob/master/autoinstaller.py


class install_if_not_found(AbstractContextManager):
    """Context manager to handle ModuleNotFoundErrors
    Adapted from contextlib.suppress
    """

    def __enter__(self):
        pass

    def __exit__(self, exctype, excinst, exctb):
        print("exctype:", exctype, isinstance(exctype, ModuleNotFoundError))
        print("excinst:", excinst, isinstance(excinst, ModuleNotFoundError))
        print("exctb:", exctb, isinstance(exctb, ModuleNotFoundError))
        if isinstance(excinst, FileNotFoundError):
            print("doing stuff")
            failed_module = re.search(r"'((?:\\'|[^'])+)'", excinst.msg).group(1)
            while True:
                resp = input(
                    f"Could not import {failed_module}. "
                    "Install? (Y)es / (n)o / (c)ustomize  "
                )
                if re.search(r"y(?:es)?", resp, flags=re.I):
                    print("Installing {failed_module}...", file=sys.stderr)
                    break
                elif re.search(r"no?", resp, flags=re.I):
                    print("Okay. Taking no action.")
                    break
                elif re.search(r"c(?:ustom)?", resp, flags=re.I):
                    install_name = input(
                        "What package name would you like to " "install? "
                    )
                    print(f"Installing {install_name}...", file=sys.stderr)
                    break
                else:
                    print('Invalid input. Type "y", "n", or "c" and press [enter].')
        return exctype is not None and isinstance(excinst, ModuleNotFoundError)


# @contextmanager
# def install_if_not_found():
#     try:
#         yield
#     except ModuleNotFoundError as e:
#         print(dir(e))
#         print(e.msg)
#         failed_module = re.search(r"'((?:\\'|[^'])+)'", e.msg).group(1)
#         while True:
#             resp = input(f'Could not import {failed_module}. '
#                          'Install? (Y)es / (n)o / (c)ustomize  ')
#             if re.search(r'y(?:es)?', resp, flags=re.I):
#                 print('Installing {failed_module}...', file=sys.stderr)
#                 break
#             elif re.search(r'no?', resp, flags=re.I):
#                 print('Okay. Taking no action.')
#                 break
#             elif re.search(r'c(?:ustom)?', resp, flags=re.I):
#                 install_name = input(f'What package name would you like to install? ')
#                 print(f'Installing {install_name}...', file=sys.stderr)
#                 break
#             else:
#                 print('Invalid input. Type "y", "n", or "c" and press [enter].')
#

with install_if_not_found():
    # TODO move this to a pytest test
    import asdfasdf1  # type: ignore  # noqa: F401
    import asdfasdf1  # noqa: F401,F811
    import asdfasdf1  # noqa: F401,F811
