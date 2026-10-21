
##@page time_integratebar Bar plot (temporal integration)
#@tableofcontents
#@section option Plotting options
# - errors
# - xpositions
# - time_period
# - op

import numpy
import pandas

from kkplot.kkengines.pythonmatplotlib.helpers import *

def _aggregate( _data, _op, _time_period) :
    data = _data.dropna()
    if _op == 'mean' :
        return data.mean(), data.mean()
    elif _op == 'sum' :
        return data.sum(), data.sum()
    elif _op == 'integrate' :
        x = [ 0.0]
        for d in range( len( data.index)-1) :
            x.append( ( data.index[d+1]-data.index[d]).total_seconds() + x[d])
        seconds = ( data.index[-1]-data.index[0]).total_seconds()
        return trapezoid( data, x) / seconds * _time_period, \
            ( trapezoid( data**2.0, x) / seconds)**0.5 * _time_period

def time_integratebar( _axes, _graph, _data, _columns, _auxcolumns, _ctx) :
    _axes.set_gid( _graph.graphid)
    error_columns = _graph.get_property( 'errors', None)
    error_columns = list( error_columns) if error_columns else error_columns
    xpositions = _graph.get_property( 'xpositions', None)
    time_period = fixed( _graph.domain.time_period( _graph.get_property( 'timeresolution', 'day')))
    op = lit( _graph.get_property( 'op', 'sum'))

    aggregated = numpy.zeros( ( len( _auxcolumns), 1+len( _auxcolumns[0])))
    errors = numpy.zeros( aggregated.shape)
    for k, ( select, groups) in enumerate( zip( _columns, _auxcolumns)) :
        if op not in ( 'mean', 'sum', 'integrate') :
            continue
        for l, group in enumerate( [ select]+groups) :
            aggregated[k,l], errors[k,l] = _aggregate( _data[group], op, time_period)

    graphlabels = [ '' if _graph.label( name) is None else lit( '%s' % ( _graph.label( name))) for name in _graph.NAMES ]
    Aggregated = pandas.DataFrame( aggregated, columns=graphlabels)
    Errors = pandas.DataFrame( errors, columns=_graph.NAMES)

    xaxis_values = [ x.replace( '__', '') for x in _graph.get_property( 'x', []) ]
    graphname = _graph.graphid.split( '.')[-1].replace( '__', '')
    if graphname in xaxis_values :
        ## sorted data frame of standardized size with dummy rows having no data
        Aggregated.index = [ graphname]
        for x in xaxis_values :
            if x != graphname :
                Aggregated = pandas.concat( [ pandas.DataFrame( numpy.nan, index=[x], columns=Aggregated.columns), Aggregated])
        Aggregated = Aggregated.sort_index()

    color = _graph.get_property( 'color', None)
    kw = kwargs( zorder=_graph.zorder, capsize=_graph.get_property( 'capsize', 0.0), \
        width=_graph.get_property( 'barwidth', 0.5), color=color)

    if len( Aggregated) > 1 :
        Aggregated.plot( ax=_axes, kind='bar', **kw)
    elif error_columns :
        error_columns = [ e-1 for e in error_columns ]
        errorbars = Errors[Errors.columns[error_columns]]
        Aggregated = Aggregated.drop( Aggregated.columns[error_columns], axis=1)
        if xpositions is None :
            xpositions = range( len( list( Aggregated.iloc[0])))
        for v in range( len( xpositions)) :
            _axes.bar( xpositions[v], Aggregated.iloc[0,v], label=graphlabels[v], yerr=errorbars.iloc[0,v], **kw)
    else :
        if xpositions is None :
            xpositions = range( len( list( Aggregated.iloc[0])))
        if color is None :
            cmap = colormap( _graph.get_property( 'colormap') or 'jet')
            colors = [ cmap( 0.25 + ( 1.0 - 0.25) * float( j)/float( len( xpositions))) for j in range( len( xpositions)) ]
            _axes.bar( xpositions, list( Aggregated.iloc[0]), color=colors, **kw)
        else :
            _axes.bar( xpositions, list( Aggregated.iloc[0]), **kw)

    return Aggregated
