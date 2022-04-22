#!/usr/bin/python

import sys
import argparse
import os
import kkplot.kkutils as utils
from kkplot.kkutils.log import *
from kkplot.kkplot_version import __version__


class kkgen_configuration( object) :

    def  __init__( self) :

        parser = argparse.ArgumentParser()

        parser.add_argument( '--names', default=None,
            help='Legend names for each data file (E.g., --names="Scenario Dry:Scenario Wet"')
## ??        parser.add_argument( '--names-pattern', default=None,
## ??            help='Legend names formed from data filename (E.g., --names-pattern=""')

        parser.add_argument( '--columns', default=':',
            help='Use specified columns (i.e., named headers) from data files. Either all columns (:), all starting at C (C:) or all from Cb to Ce (Cb:Ce), or single columns delimited by comma (E.g., --columns="dN_no_emis:dN_nh3_emis,dN_n2_emis")')
        parser.add_argument( '--columns-delim', default='\t',
            help='Data file columns delimiter (default=<TAB>)')
        parser.add_argument( '--show-columns', action='store_true',default=False,
            help='Dump canonicalized column names to stdout')

        parser.add_argument( '--outputformat', default='yaml',
            help='File format for resulting script')
        parser.add_argument( '--diff', action='store_true',default=False,
            help='Generate difference script for data files')

        parser.add_argument( '--title', default='null',
            help='Plot title (default none)')
        parser.add_argument( '--range', default='RANGE',
            help='Range to plot. E.g., time period (default RANGE)')

        parser.add_argument( '--debug', action='store_true', default=False,
            help='Switch on debug mode')


        parser.add_argument( '-V', '--version', action='store_true', default=False,
            help='show version')


        parser.add_argument( 'datafiles', nargs='*', default='-',
            help='Data files (default="-" (stdin))')

        self.args = parser.parse_args()

        kklog.set_debug( self.args.debug)
        kklog.set_color( self.args.debug)

        self.opts = dict()

    @property
    def  showversion( self) :
        return  self.args.version

    @property
    def  datafiles( self) :
        return  self.args.datafiles

    @property
    def  names( self) :
        names = [] if self.args.names is None else self.args.names.split( ':')
        d = len(self.datafiles)
        n = len(names)
        return names + [ '%d'%(r+n) for r in range(max(0, d-n)) ]

    @property
    def  columns( self) :
        return  self.args.columns
    @property
    def  columnsdelim( self) :
        return  self.args.columns_delim
    @property
    def  showcolumns( self) :
        return  self.args.show_columns

    @property
    def  diff( self) :
        return  self.args.diff

    @property
    def  outputformat( self) :
        return  self.args.outputformat

    @property
    def  engine( self) :
        return 'matplotlib'
    @property
    def  title( self) :
        if  self.args.title=='null' :
            return 'null'
        return '"%s"' % ( self.args.title)
    @property
    def  range( self) :
        return  self.args.range

def canonicalizename( _name) :
    validchars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789'
    name = _name.strip( ' \t./\\')
    canonicalized_name = ''
    for c in name :
        if not c in validchars :
            canonicalized_name += '_'
        else :
            canonicalized_name += c
    return canonicalized_name

def datasourceid( _filename, _slot) :
    f = '%s_%05d' % ( _filename[_filename.rfind(os.sep)+1:].strip(), _slot)
    return canonicalizename( f)


def readheader( _filename, _delim) :
    F = open( _filename, 'r')
    H = F.readline()
    F.close()
    H = H.split( _delim)
    unit_offs = lambda L, pos : L if pos == -1 else pos
    return [ c[:unit_offs( len(c), c.find( '['))] for c in H ]

def findplotheaders( _header, _columns) :
    if _columns[0] == '+' :
        return _header[_header.index(_columns[1:])+1:]
    C = list()
    columns = _columns.split( ',')
    ## example: columns="c1,c2,c3:c4,c5:"
    for column_range in columns :
        if ':' in column_range :
            c1, c2 = column_range.split( ':')
            if c1 == '' and c2 == '' :
                C += _header[:]
            if c2 == '' :
                C += _header[_header.index( c1):]
            else :
                C += _header[_header.index( c1):_header.index( c2)+1]
        else :
            C.append( _header[_header.index( column_range)])
    kklog_debug( 'plot-headers='+str(C))
    return C


def kkscript_preamble( _config) :
    return 'engine: \"%s\"' % ( _config.engine)

def kkscript_datasources( _config) :
    D = list()
    for l, f in enumerate( _config.datafiles) :
        fid = datasourceid( f, l)
        D.append( '  %s:\n    path: \"%s\"' % ( fid, f))
    return 'datasources:\n%s' % ( '\n'.join( D))


def kkscript_figureproperties( _config) :
    fig_opts = _config.opts
    if fig_opts is None :
        fig_opts = dict()
    o = lambda _key, _default : str(fig_opts.get( _key, _default))
    return '''
figure:
  title: %s
  time: '%s'
  output: 'output.pdf'
  properties:
    #colorscheme: grayscale
    alignmentorder: 'rowsfirstdownward'
    square: %s
    columns: %s
    rows: %s
    height: %s
    width: %s
    legendfontsize: 10
''' % ( _config.title, _config.range, o('square','false'), o('columns',0), o('rows',0), o('height','null'), o('width','null'))

def kkscript_plots_separate( _config) :
    graphs = list()
    for l, fname in enumerate( _config.datafiles) :
        fid = datasourceid( fname, l)
        fheader = readheader( fname, _config.columnsdelim)
        fcolumns = findplotheaders( fheader, _config.columns)
        for column in fcolumns :
            graphs.append( '- %s:\n      graphs:\n        - %s:\n            name: [ \"%s@%s\" ]\n            label: \"%s\"' \
                % ( '%s_%s' % ( column, fid), column, column, fid, column.replace( '_', ' ').title()))

    return 'plots:\n  %s' % ( '\n  '.join( graphs))

def kkscript_plots_diff( _config) :
    graphs = list()
    fheader = readheader( _config.datafiles[0], _config.columnsdelim)
    fcolumns = findplotheaders( fheader, _config.columns)
    for column in fcolumns :
        graph = '- %s:\n      graphs:\n' % ( column)
        D = len( _config.datafiles)
        for l, fname in enumerate( _config.datafiles) :
            fid = datasourceid( fname, l)
            lblname = _config.names[D-l-1]
            graph += '        - %s:\n            name: [ \"%s@%s\" ]\n            label: \"%s [%s]\"\n' \
                % ( '%s_%s' % ( column, fid), column, fid, column.replace( '_', ' ').title(), lblname)

        graphs.append( graph)

    return 'plots:\n  %s' % ( '\n  '.join( graphs))

def kkgen_showcolumns( _config) :
    for l, fname in enumerate( _config.datafiles) :
        header = readheader( fname, _config.columnsdelim)
        columns = findplotheaders( header, _config.columns)
        print '%s:' % ( fname)
        print '  '+'\n  '.join( [ '%3d  %s'%(i+1,n) for i, n in enumerate( columns)])
 
def kkscript_plots( _config) :
    if _config.diff :
        return kkscript_plots_diff( _config)
    return kkscript_plots_separate( _config)

def kkgen_generate( _config, _plot_fn) :
    kklog_debug( 'files=%s' % ( str(_config.datafiles)))
    kklog_debug( 'columns=%s' % ( _config.columns))

    if _config.showcolumns :
        kkgen_showcolumns( _config)
    else :
        plots = _plot_fn( _config)
        print kkscript_preamble( _config)
        print '\n'
        print kkscript_datasources( _config)
        print '\n'
        print kkscript_figureproperties( _config)
        print '\n'
        print plots


def main( _plot_fn=None, _fig_opts=dict()) :
    try :
        kkgen_config = kkgen_configuration()
    except :
        return 65

    kkgen_config.opts.update( _fig_opts)
    if kkgen_config.showversion :
        sys.stdout.write( '%s %s\n' % ( utils.programname(), str(__version__)))
    else :
        plot_fn = _plot_fn
        if plot_fn is None :
            plot_fn = kkscript_plots
        kkgen_generate( kkgen_config, plot_fn)
    return 0

if __name__ == '__main__':

    rc = main()
    sys.exit( rc)

