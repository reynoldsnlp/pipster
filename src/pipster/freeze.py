import subprocess
import sys
from typing import List

try:
    from pip._internal.commands.freeze import FreezeCommand
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        f"Please install pip for the current interpreter: {sys.executable}"
    )

from .utils import pip_help_with_python_kwargs
from .utils import build_cmd

__all__ = ["freeze"]
freeze_cmd = FreezeCommand(name="Freeze", summary="Provides parse_args.")


def freeze(*args, **kwargs) -> List[str]:
    cli_args = build_cmd("freeze", *args, **kwargs)
    print("Running `", " ".join(cli_args), "`  ...", file=sys.stderr)
    cli_cmd = [sys.executable, "-m"] + cli_args
    result = subprocess.run(cli_cmd, capture_output=True, check=True, text=True)
    return result.stdout.strip().split("\n")


freeze.__doc__ += pip_help_with_python_kwargs("freeze", freeze_cmd)
