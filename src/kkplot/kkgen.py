#!/usr/bin/env python3
import sys
import argparse
import os

import kkplot.kkutils as utils
from kkplot.kkutils.log import *
from kkplot.kkplot_version import __version__


class KKGenConfiguration:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--names",
            default=None,
            help=(
                'Legend names for each data file '
                '(e.g., --names="Scenario Dry:Scenario Wet")'
            ),
        )
        parser.add_argument(
            "--columns",
            default=":",
            help=(
                "Use specified columns (named headers) from data files. Either all "
                "columns (:), all starting at C (C:) or all from Cb to Ce (Cb:Ce), or "
                "single columns delimited by comma "
                '(e.g., --columns="dN_no_emis:dN_nh3_emis,dN_n2_emis")'
            ),
        )
        parser.add_argument(
            "--columns-delim",
            default="\t",
            help="Data file columns delimiter (default=<TAB>)",
        )
        parser.add_argument(
            "--show-columns",
            action="store_true",
            default=False,
            help="Dump canonicalized column names to stdout",
        )
        parser.add_argument(
            "--outputformat",
            default="yaml",
            help="File format for resulting script",
        )
        parser.add_argument(
            "--diff",
            action="store_true",
            default=False,
            help="Generate difference script for data files",
        )
        parser.add_argument(
            "--title",
            default="null",
            help="Plot title (default none)",
        )
        parser.add_argument(
            "--range",
            dest="range_",
            default="RANGE",
            help="Range to plot, e.g. time period (default RANGE)",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            default=False,
            help="Switch on debug mode",
        )
        parser.add_argument(
            "-V",
            "--version",
            action="store_true",
            default=False,
            help="Show version",
        )
        parser.add_argument(
            "datafiles",
            nargs="*",
            default=["-"],
            help='Data files (default="-" (stdin))',
        )

        self.args = parser.parse_args()

        kklog.set_debug(self.args.debug)
        kklog.set_color(self.args.debug)

        # additional figure options that can be passed from main()
        self.opts = {}

    @property
    def showversion(self):
        return self.args.version

    @property
    def datafiles(self):
        return self.args.datafiles

    @property
    def names(self):
        names = [] if self.args.names is None else self.args.names.split(":")
        d = len(self.datafiles)
        n = len(names)
        # fill up missing names with numeric labels
        return names + [f"{r + n}" for r in range(max(0, d - n))]

    @property
    def columns(self):
        return self.args.columns

    @property
    def columnsdelim(self):
        return self.args.columns_delim

    @property
    def showcolumns(self):
        return self.args.show_columns

    @property
    def diff(self):
        return self.args.diff

    @property
    def outputformat(self):
        return self.args.outputformat

    @property
    def engine(self):
        return "matplotlib"

    @property
    def title(self):
        if self.args.title == "null":
            return "null"
        return f'"{self.args.title}"'

    @property
    def range(self):
        return self.args.range_


def canonicalizename(name_raw: str) -> str:
    validchars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789"
    name = name_raw.strip(" \t./\\")
    return "".join(c if c in validchars else "_" for c in name)


def datasourceid(filename: str, slot: int) -> str:
    base = filename[filename.rfind(os.sep) + 1 :].strip()
    f = f"{base}_{slot:05d}"
    return canonicalizename(f)


def readheader(filename: str, delim: str):
    with open(filename, "r", encoding="utf-8") as f:
        header_line = f.readline()
    cols = header_line.split(delim)

    def unit_offs(length, pos):
        return length if pos == -1 else pos

    return [c[: unit_offs(len(c), c.find("["))] for c in cols]


def findplotheaders(header, columns_str):
    if columns_str[0] == "+":
        # all columns after a given one
        base = columns_str[1:]
        return header[header.index(base) + 1 :]

    selected = []
    columns = columns_str.split(",")
    # example: columns="c1,c2,c3:c4,c5:"
    for column_range in columns:
        if ":" in column_range:
            c1, c2 = column_range.split(":")
            if c1 == "" and c2 == "":
                selected += header[:]
            elif c2 == "":
                selected += header[header.index(c1) :]
            else:
                selected += header[header.index(c1) : header.index(c2) + 1]
        else:
            selected.append(header[header.index(column_range)])
    kklog_debug("plot-headers=" + str(selected))
    return selected


def kkscript_preamble(config: KKGenConfiguration) -> str:
    return f'engine: "{config.engine}"'


def kkscript_datasources(config: KKGenConfiguration) -> str:
    lines = []
    for i, fname in enumerate(config.datafiles):
        fid = datasourceid(fname, i)
        lines.append(f'  {fid}:\n    path: "{fname}"')
    return "datasources:\n" + "\n".join(lines)


def kkscript_figureproperties(config: KKGenConfiguration) -> str:
    fig_opts = config.opts or {}
    o = lambda key, default: str(fig_opts.get(key, default))

    return f"""
figure:
  title: {config.title}
  time: '{config.range}'
  output: 'output.pdf'
  properties:
    #colorscheme: grayscale
    alignmentorder: 'rowsfirstdownward'
    square: {o('square', 'false')}
    columns: {o('columns', 0)}
    rows: {o('rows', 0)}
    height: {o('height', 'null')}
    width: {o('width', 'null')}
    legendfontsize: 10
""".lstrip("\n")


def kkscript_plots_separate(config: KKGenConfiguration) -> str:
    graphs = []
    for i, fname in enumerate(config.datafiles):
        fid = datasourceid(fname, i)
        header = readheader(fname, config.columnsdelim)
        columns = findplotheaders(header, config.columns)
        for column in columns:
            label = column.replace("_", " ").title()
            graphs.append(
                f"- {column}_{fid}:\n"
                f"      graphs:\n"
                f"        - {column}:\n"
                f"            name: [ \"{column}@{fid}\" ]\n"
                f"            label: \"{label}\""
            )
    return "plots:\n  " + "\n  ".join(graphs)


def kkscript_plots_diff(config: KKGenConfiguration) -> str:
    graphs = []
    header = readheader(config.datafiles[0], config.columnsdelim)
    columns = findplotheaders(header, config.columns)
    D = len(config.datafiles)
    for column in columns:
        graph = f"- {column}:\n      graphs:\n"
        for i, fname in enumerate(config.datafiles):
            fid = datasourceid(fname, i)
            lblname = config.names[D - i - 1]
            label = column.replace("_", " ").title()
            graph += (
                f"        - {column}_{fid}:\n"
                f"            name: [ \"{column}@{fid}\" ]\n"
                f"            label: \"{label} [{lblname}]\"\n"
            )
        graphs.append(graph.rstrip("\n"))
    return "plots:\n  " + "\n  ".join(graphs)


def kkgen_showcolumns(config: KKGenConfiguration) -> None:
    for fname in config.datafiles:
        header = readheader(fname, config.columnsdelim)
        columns = findplotheaders(header, config.columns)
        print(f"{fname}:")
        for i, name in enumerate(columns, start=1):
            print(f"  {i:3d}  {name}")


def kkscript_plots(config: KKGenConfiguration) -> str:
    if config.diff:
        return kkscript_plots_diff(config)
    return kkscript_plots_separate(config)


def kkgen_generate(config: KKGenConfiguration, plot_fn) -> None:
    kklog_debug("files=%s" % str(config.datafiles))
    kklog_debug("columns=%s" % config.columns)
    if config.showcolumns:
        kkgen_showcolumns(config)
    else:
        plots = plot_fn(config)
        print(kkscript_preamble(config))
        print()
        print(kkscript_datasources(config))
        print()
        print(kkscript_figureproperties(config))
        print()
        print(plots)


def main(plot_fn=None, fig_opts=None) -> int:
    if fig_opts is None:
        fig_opts = {}

    try:
        config = KKGenConfiguration()
    except Exception:
        # 65 is EX_DATAERR in sysexits.h; keep behavior if you rely on it
        return 65

    config.opts.update(fig_opts)

    if config.showversion:
        sys.stdout.write(f"{utils.programname()} {__version__}\n")
        return 0

    if plot_fn is None:
        plot_fn = kkscript_plots

    kkgen_generate(config, plot_fn)
    return 0


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
