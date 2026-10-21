
import numpy

from kkplot.kkengines.pythonmatplotlib.helpers import *

def time_heatmap( _axes, _graph, _data, _columns, _auxcolumns, _ctx) :
    _axes.set_gid( _graph.graphid)

    data = _data[_columns][_data[_columns[0]].notnull()]
    c = numpy.array( data.T.values)
    c_min = _graph.get_property( 'colorbarlimitlow')
    c_min = numpy.nanmin( c) if c_min is None else c_min
    c_max = _graph.get_property( 'colorbarlimithigh')
    c_max = numpy.nanmax( c) if c_max is None else c_max
    if numpy.isnan( c_min) or numpy.isnan( c_max) :
        print( '[WW] no valid data for graph; ignoring')
        return

    x = data.index
    levels = _data[[ aux[0] for aux in _auxcolumns]]
    y = numpy.array( levels.loc[levels.first_valid_index()].T.values)
    ## allow for plots including nan-values
    invalid = numpy.isnan( y)
    y, c = y[~invalid], c[~invalid]

    cmap = 'gray' if _ctx.dviplot.get_property( 'colorscheme') == 'grayscale' else 'Oranges'
    kkheatmap = _axes.pcolormesh( x, y, c, cmap=colormap( _graph.get_property( 'colormap', cmap)), \
        vmin=c_min, vmax=c_max, **kwargs( shading=_graph.get_property( 'shading', 'auto'), zorder=_graph.zorder))

    ## label used to be a raw string literal (r"...")
    label = _graph.get_property( 'colorbarlabel', _graph.labelat( 0, ''))
    if not isinstance( label, str) :
        raise NameError( 'invalid colorbar label "%s"' % ( label))
    _axes.get_figure().colorbar( kkheatmap, ax=_axes, label=label, **kwargs( \
        pad=_graph.get_property( 'colorbarpad'),
        orientation=_graph.get_property( 'colorbarorientation', 'horizontal')))

    annotation = lit( '%s' % ( _graph.get_property( 'annotate', 'None')))
    if annotation != 'None' :
        for Xi, X in enumerate( x) :
            for Yi, Y in enumerate( y) :
                if not numpy.isnan( c[Yi][Xi]) :
                    _axes.plot( X, Y, annotation, markerfacecolor='none', color='black')
    _axes.xaxis_date()
