"""Formatter to display `pip install` help with python kwargs"""

from optparse import Option
import re
from typing import Any

from pip._internal.cli.parser import UpdatingDefaultsHelpFormatter
from pip._internal.cli.parser import PrettyHelpFormatter


class PythonHelpFormatter(UpdatingDefaultsHelpFormatter):
    """Formatter for optparse that transforms CLI options to python arguments."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # help position must be aligned with __init__.parseopts.description
        kwargs["max_help_position"] = 30
        kwargs["indent_increment"] = 1
        # kwargs["width"] = shutil.get_terminal_size()[0] - 4  # dynamic
        kwargs["width"] = 72
        super(PrettyHelpFormatter, self).__init__(*args, **kwargs)

    def _format_option_strings(
        self, option: Option, mvarfmt: str = '="<{}>"', optsep: str = ", "
    ) -> str:
        """
        Return a comma-separated list of option strings and metavars.

        :param option:  tuple of (short opt, long opt), e.g: ('-f', '--format')
        :param mvarfmt: metavar format string
        :param optsep:  separator
        """
        if option.help:
            option_refs = sorted(
                set(re.findall(r"--[a-z]+(?:-[0-9a-z]+)*", option.help)),
                key=len,
                reverse=True,
            )
            for ref in option_refs:
                keyword = ref[2:].replace("-", "_")
                if keyword.startswith("no_"):
                    keyword = keyword[3:] + "=False"
                option.help = option.help.replace(ref, f"`{keyword}`")

        mult_mvarfmt = '=["<{}1>", "<{}2>"]'

        multiple = option.action == "append"
        additive = option.action == "count"

        opts = []
        multiples = []
        metavar = None
        if option.takes_value():
            assert option.dest is not None
            metavar = option.metavar or option.dest
            metavar = metavar.lower()

        if option._short_opts:
            opt = option._short_opts[0].lstrip("-")
            if metavar:
                opts.append(opt)
                opts.append(mvarfmt.format(metavar))
                if multiple:
                    multiples.append(opt)
                    multiples.append(mult_mvarfmt.format(metavar, metavar))
            elif additive:
                opts.append(f"{opt}=1, {opt}=2, {opt}=3")
            else:
                opts.append(f"{opt}=True")

            if option._long_opts:  # add optsep if there is a long option, too
                opts.append(optsep)

        if option._long_opts:
            opt = option._long_opts[0].lstrip("-").replace("-", "_")
            if opt.startswith("no_"):
                opts.append(f"{opt[3:]}=False")
            elif additive:
                opts.append(f"{opt}={{1/2/3}}")
            elif metavar:
                opts.append(opt)
                opts.append(mvarfmt.format(metavar))
                if multiple:
                    if multiples:
                        multiples.append(optsep)
                    multiples.append(opt)
                    multiples.append(mult_mvarfmt.format(metavar, metavar))
            else:
                opts.append(f"{opt}=True")

        if multiples:
            opts.append(",\n  ")
            opts.extend(multiples)

        return "".join(opts)
