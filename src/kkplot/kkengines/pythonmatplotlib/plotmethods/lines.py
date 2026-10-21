
import numpy

from kkplot.kkutils.log import *
from kkplot.kkengines.pythonmatplotlib.helpers import *

def time_line( _axes, _graph, _data, _columns, _auxcolumns, _ctx) :
    _axes.set_gid( _graph.graphid)
    columns = _columns + [ c for aux in _auxcolumns for c in aux ]
    graphlabels = column_labels( _graph, columns)
    for column in columns :
        if graphlabels[column].strip().startswith( '@') :
            kklog_warn( 'label functions (%s) are not supported by the matplotlib engine' % ( graphlabels[column]))

    smoothen = _graph.get_property( 'interpolate', False)
    parametric = find_columns( [ 'x-axis'], columns)
    if parametric :
        x = _data[parametric[0]]
        columns.remove( parametric[0])
    else :
        x = _data['row'] if smoothen else _data.index

    c_lo, c_hi = ( 0.25, 1)
    cmap = _graph.get_property( 'colormap') if not _graph.get_property( 'color') else None
    regression = _graph.get_property( 'regression', False)

    for j, column in enumerate( columns) :
        xs, ys = x.values, _data[column].values
        if smoothen :
            from scipy import interpolate
            tck, u = interpolate.splprep( [ x, _data[column]], s=1)
            xs, ys = interpolate.splev( numpy.arange( 0.0, 1.0, 0.0001), tck)

        color = dict()
        if cmap :
            color = dict( color=colormap( cmap)( c_lo + ( c_hi - c_lo) * float( j)/float( len( columns))))
        _axes.plot( xs, ys, **color, **line_kwargs( _graph), label=graphlabels[column], gid=column)

        if regression :
            from sklearn.linear_model import LinearRegression
            import pandas
            X = numpy.array( [ pandas.to_datetime( d).toordinal() for d in xs]).reshape( -1, 1)
            model = LinearRegression()
            model.fit( X, ys)
            _axes.plot( xs, model.predict( X), **color, **line_kwargs( _graph, linestyle='dashed'), label='', gid=column)
            textcoordinates = [ fixed( c) for c in _graph.get_property( 'textcoordinates', [0.05, 0.8])]
            slope = model.coef_[0] * ( X[1]-X[0])
            _axes.annotate( 'slope: %.1f' % ( slope), xy=( 0.0, 0.0), xycoords='axes fraction', \
                xytext=textcoordinates, textcoords=lit( _graph.get_property( 'textcoords', 'axes fraction')))

    return xs, ys

def time_points( _axes, _graph, _data, _columns, _auxcolumns, _ctx) :
    _graph.add_properties( { 'linewidth': 0.0})
    if _graph.get_property( 'marker') is None :
        _graph.add_properties( { 'marker': '.'})
    return time_line( _axes, _graph, _data, _columns, _auxcolumns, _ctx)

def time_points_errors( _axes, _graph, _data, _columns, _auxcolumns, _ctx) :
    _axes.set_gid( _graph.graphid)
    graphlabels = column_labels( _graph, _columns)
    kw = line_kwargs( _graph,
        capsize=_graph.get_property( 'capsize'),
        linewidth=_graph.get_property( 'linewidth', 0.0),
        elinewidth=_graph.get_property( 'elinewidth', 1.0),
        marker=_graph.get_property( 'marker', '.'))
    for column, yerr in zip( _columns, [ aux[0] for aux in _auxcolumns]) :
        _axes.errorbar( _data.index.values, _data[column].values, yerr=_data[yerr], **kw, \
            label=graphlabels[column], gid=column)

def time_cumulativeline( _axes, _graph, _data, _columns, _auxcolumns, _ctx) :
    _axes.set_gid( _graph.graphid)
    graphlabels = column_labels( _graph, _columns)
    for column in _columns :
        _axes.plot( _data.index, _data[column].cumsum().values, **line_kwargs( _graph), \
            label=graphlabels[column], gid=column)

def time_bars( _axes, _graph, _data, _columns, _auxcolumns, _ctx) :
    _axes.set_gid( _graph.graphid)
    graphlabels = column_labels( _graph, _columns)
    color = _graph.get_property( 'color')
    for column in _columns :
        _axes.bar( _data.index, _data[column].values, \
            **kwargs( zorder=_graph.zorder, color=color, edgecolor=color, facecolor=color), \
            label=graphlabels[column], gid=column)
    _axes.xaxis_date()

def time_scatter_columns( _columns, _auxcolumns) :
    columns = _columns + [ c for aux in _auxcolumns for c in aux ]
    xy = find_columns( [ 'x', 'y'], columns)
    if len( xy) != 2 :
        kklog_error( 'Plot method "scatter" requires (x, y) columns')
        return None
    return xy

def time_scatter( _axes, _graph, _data, _columns, _auxcolumns, _ctx) :
    _axes.set_gid( _graph.graphid)
    x, y = time_scatter_columns( _columns, _auxcolumns)
    _axes.scatter( _data[x], _data[y], **kwargs(
        color=_graph.get_property( 'color'),
        linewidth=_graph.get_property( 'linewidth'),
        marker=_graph.get_property( 'marker'),
        markersize=_graph.get_property( 'markersize'),
        markeredgecolor=_graph.get_property( 'markeredgecolor'),
        markeredgewidth=_graph.get_property( 'markeredgewidth'),
        markerfacecolor=_graph.get_property( 'markercolor'),
        markevery=_graph.get_property( 'markerstride'),
        zorder=_graph.zorder), label=lit( _graph.labelat( 0)))
