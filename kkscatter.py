
##  example calls:
##  python kkscatter.py --range '1996-01-01->2012-01-01' --title 'Scatter Plot' --columns dC_ch4_emis: soilchemistry-daily.txt | kkplot -
##
##  diff mode:
##  python kkscatter.py --range '1996-01-01->2012-01-01' --title 'Scatter Plot' --columns dC_ch4_emis: soilchemistry-daily.txt | kkplot -

import sys
import kkgen as gen
from kkutils.log import *
from kkutils import colors

def label( _j, _J=0) :
    if _j==_J :
        return lambda _lbl : '"%s"' % _lbl.replace( '_', ' ').title().replace( ' ', '')
    return lambda _lbl : 'null'
def field( _column_r, _column_c, _file) :
    if _column_r == _column_c :
        return '"x=%s@%s"' % ( _column_r, _file)
    return '"x=%s@%s", "y=%s@%s"' % ( _column_r, _file, _column_c, _file)

import kkutils as utils
def layout( _n_files) :
    M, N = utils.auto_layout( _n_files)
    kklog_debug( "file-layout= %d,%d for %d files" % ( M,N, _n_files))
    if M*N > _n_files :
        return M*N, 1
    return M, N

def kkscatter_plots_separate( _config) :
    graphs = list()
    F = len(_config.datafiles)
    colorset = colors.MakeColorVector( F)
    M, N = layout( F)
    n_columns = 1 ## assume at least one column.. :|
    for m in range( M) :
        r = 0
        while r < n_columns :
            for l, fname in enumerate( _config.datafiles[m*N:(m+1)*N]) :
                fid = gen.datasourceid( fname, m*N+l)
                header = gen.readheader( fname, _config.columnsdelim)
                columns = gen.findplotheaders( header, _config.columns)
                n_columns = max( n_columns, len( columns))

                C = lambda i : columns[i]

                Lx = label( r, len(columns)-1)
                c = 0
                while c < n_columns :
                    Ly = label( c, 0)
                    G = '%s_%s' % ( C(r), C(c))
                    xticks = '' if (r+1)==len(columns) else "xticks: null,"
                    yticks = '' if c==0 else "yticks: null,"
                    kind = 'histogram' if c==r else 'scatter'
                    graphs.append( '- %s:\n      properties: { kind: \"%s\", xlabel: %s, ylabel: %s, %s %s square: true, align: false }\n      graphs:\n        - %s:\n            name: [ %s ]\n            label: null\n            properties: { color: "%s" }\n' \
                        % ( '%s_%s' % ( G, fid), kind, Lx(C(c)),Ly(C(r)), xticks,yticks, G, field(C(r),C(c),fid), colorset[m*N+l]))
                    c += 1
            r += 1

    _config.opts['columns'] = N*n_columns
    _config.opts['rows'] = M*n_columns
    _config.opts['width'] = N*n_columns*3.0
    _config.opts['height'] = M*n_columns*3.0
    if M != N :
        _config.opts['square'] = 'null'
    return 'plots:\n  %s' % ( '\n  '.join( graphs))

def kkscatter_plots_diff( _config) :
    graphs = list()
    header = gen.readheader( _config.datafiles[0], _config.columnsdelim)
    columns = gen.findplotheaders( header, _config.columns)
    kklog_debug( 'columns='+str(columns))
    colorset = colors.MakeColorVector( len(_config.datafiles))
    for r, column_r in enumerate( columns) :
        Lx = label( r, len(columns)-1)
        xticks = '' if (r+1)==len(columns) else "xticks: null,"
        for c, column_c in enumerate( columns) :
            Ly = label( c, 0)
            yticks = '' if c==0 else "yticks: null,"
            kind = 'histogram' if c==r else 'scatter'
            graph  = '- %s:\n      properties: { kind: \"%s\", xlabel: %s, ylabel: %s, %s %s square: true, align: false }\n' \
                % ( '%s_%s' % ( column_r, column_c), kind, Lx(column_c),Ly(column_r), xticks,yticks)
            graph += '      graphs:\n'
            D = len( _config.datafiles)
            for l, fname in enumerate( _config.datafiles) :
                fid = gen.datasourceid( fname, l)
                lblname = _config.names[D-l-1]
                graph += '        - %s:\n            name: [ %s ]\n            label: [ \"%s\" ]\n            properties: { color: "%s" }\n' \
                    % ( fid, field(column_r,column_c,fid), lblname, colorset[l])
            graphs.append( graph)
    return 'plots:\n  %s' % ( '\n  '.join( graphs))

def kkscatter_plot( _config) :
    if _config.diff :
        return kkscatter_plots_diff( _config)
    return kkscatter_plots_separate( _config)


if __name__ == '__main__':

    fig_opts = { 'square':'true' }
    rc = gen.main( kkscatter_plot, fig_opts)
    sys.exit( rc)

