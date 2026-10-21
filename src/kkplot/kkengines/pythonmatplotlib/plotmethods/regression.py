
import numpy
import pandas

from kkplot.kkengines.pythonmatplotlib.helpers import *

def _reduce( _data, _column, _other, _graph, _time_period, _timeresolution) :
    """reduce time series "_column" to a single value"""
    setop = _graph.get_property( 'setop', 'union')
    op = _graph.get_property( 'op', 'integrate')
    if setop == 'union' :
        data = _data[_column].loc[_data[_column].notnull()]
        nodes = numpy.array( [ 0]+[ getattr( timedelta( data.index[i+1]-data.index[i]), _timeresolution+'s') \
            for i in range( len( data.index)-1)]).cumsum()
    elif setop == 'intersect' and op == 'integrate' :
        data = _data[_column].copy()
        data.loc[ _data[_column].isnull()|_data[_other].isnull()] = 0.0
        nodes = _data.index
    elif setop == 'intersect' and op in ( 'mean', 'max') :
        data = _data[_column].loc[_data[_column].notnull()&_data[_other].notnull()]
    else :
        raise NameError( 'unsupported set operation "%s" (op=%s)' % ( setop, op))

    if op == 'integrate' :
        point = trapezoid( data, x=nodes)
        return point / getattr( timeperiod( data.index[-1]-data.index[0]), _timeresolution+'s') * _time_period
    elif op == 'mean' :
        return data.mean()
    elif op == 'max' :
        return data.max()
    return data

def time_regressionpoint( _axes, _graph, _data, _columns, _auxcolumns, _ctx) :
    _axes.set_gid( _graph.graphid)
    timeresolution = _graph.get_property( 'timeresolution', 'day')
    time_period = fixed( _graph.domain.time_period( timeresolution))

    data_column_x, data_column_y = _columns[0], _auxcolumns[0][0]
    point_x = _reduce( _data, data_column_x, data_column_y, _graph, time_period, timeresolution)
    point_y = _reduce( _data, data_column_y, data_column_x, _graph, time_period, timeresolution)

    label = lit( _graph.label( _columns[0]))
    common = kwargs(
        zorder=_graph.zorder,
        marker=_graph.get_property( 'marker', 'o'),
        markersize=_graph.get_property( 'markersize'),
        markeredgecolor=_graph.get_property( 'markeredgecolor'),
        markeredgewidth=_graph.get_property( 'markeredgewidth'),
        markerfacecolor=_graph.get_property( 'markercolor'))

    if _graph.get_property( 'op') == 'all' :
        concat = pandas.concat( [ _data[c].dropna() for c in _data.columns], axis=1, join='inner')
        _axes.plot( concat[data_column_x], concat[data_column_y], **common, \
            **kwargs( color=_graph.get_property( 'color'), linewidth=0.0), label='%s' % ( label), gid=data_column_x)
        return [ ( concat[data_column_x], concat[data_column_y])]

    if _graph.get_property( 'xerror') is None and _graph.get_property( 'yerror') is None :
        _axes.plot( point_x, point_y, **common, \
            **kwargs( color=_graph.get_property( 'color'), linewidth=_graph.get_property( 'linewidth')), \
            label='_%s' % ( label), gid=data_column_x)
    else :
        _axes.errorbar( point_x, point_y, fmt='', **common, **kwargs(
            xerr=_graph.get_property( 'xerror'),
            yerr=_graph.get_property( 'yerror'),
            capsize=_graph.get_property( 'capsize'),
            ecolor=_graph.get_property( 'color'),
            elinewidth=_graph.get_property( 'linewidth')))

    return [ ( point_x, point_y)]

def _aslist( _points) :
    try :
        iter( _points)
        return _points.tolist()
    except Exception :
        return [ _points]

def _collect_points( _graph, _columns, _auxcolumns, _graphresults) :
    """gather (x, y) pairs produced by the regression point graphs this graph depends on"""
    columns = _columns + [ c for aux in _auxcolumns for c in aux ]
    x, y = list(), list()
    for column in columns :
        if _graph.is_graphresult( column) :
            continue
        for points_name in _graph.dependencies( column) :
            for points in _graphresults[points_name] :
                x.append( _aslist( points[0]))
                y.append( _aslist( points[1]))
    ## flatten lists if points contain lists
    x = [ a for b in x for a in b]
    y = [ a for b in y for a in b]
    return pandas.Series( x), pandas.Series( y)

def time_regressionline( _axes, _graph, _data, _columns, _auxcolumns, _ctx) :
    import statsmodels.api as sm

    _axes.set_gid( _graph.graphid)
    graphid = _graph.graphid
    x, y = _collect_points( _graph, _columns, _auxcolumns, _ctx.graphresults)
    rmse = numpy.sqrt( numpy.mean( numpy.square( y-x)))
    rrmse = _graph.get_property( 'rrmse', '')
    if rrmse == 'x' :
        rrmse = rmse / numpy.mean( x)
    elif rrmse == 'y' :
        rrmse = rmse / numpy.mean( y)
    bias = numpy.mean( y-x)

    x = sm.add_constant( x)
    regression_model = sm.OLS( y, x).fit()
    textcoordinates = [ fixed( c) for c in _graph.get_property( 'textcoordinates', [0.05, 0.8])]
    textcoords = lit( _graph.get_property( 'textcoords', 'axes fraction'))

    _axes.plot( x.iloc[:,1], regression_model.fittedvalues, **kwargs(
        zorder=_graph.zorder,
        linestyle=linestyle( _graph.get_property( 'linestyle', 'solid')),
        linewidth=_graph.get_property( 'linewidth'),
        color=_graph.get_property( 'color')), label='_%s' % ( graphid), gid=graphid)
    upper_limit = max( _axes.get_xlim()[1], _axes.get_ylim()[1])
    lower_limit = min( _axes.get_xlim()[0], _axes.get_ylim()[0])
    _axes.plot( [ lower_limit, upper_limit], [ lower_limit, upper_limit], color='grey', linestyle='dashed')

    name = lit( '%s' % ( _graph.get_property( 'name', '')))
    params = regression_model.params
    text = 'r$^2$: %.2f %s\ny=%.1f+%.2fx\nRMSE = %.2f\n' % ( regression_model.rsquared, name, params['const'], params[0], rmse)
    if _graph.get_property( 'rrmse', '') in [ 'x', 'y'] :
        text += 'RRMSE = %.2f\n' % ( rrmse)
    text += 'bias = %.1f' % ( bias)
    _axes.annotate( text, xy=( 0.0, 0.0), xycoords='axes fraction', xytext=textcoordinates, textcoords=textcoords)

    return regression_model

def time_regressionzero( _axes, _graph, _data, _columns, _auxcolumns, _ctx) :
    import statsmodels.api as sm

    _axes.set_gid( _graph.graphid)
    graphid = _graph.graphid
    x, y = _collect_points( _graph, _columns, _auxcolumns, _ctx.graphresults)

    regression_model = sm.OLS( y, x).fit()
    _axes.plot( x, regression_model.predict( x), **kwargs(
        zorder=_graph.zorder,
        linestyle=linestyle( _graph.get_property( 'linestyle', 'solid')),
        linewidth=_graph.get_property( 'linewidth'),
        color=_graph.get_property( 'color')), label='_%s' % ( graphid), gid=graphid)
    _axes.plot( [ 0.0, 1000.0], [ 0.0, 1000.0], label='', gid=graphid, color='black', linestyle='dashed')

    f = regression_model.predict( x)
    m = '%.2f' % ( ( f.iloc[-1]-f.iloc[0]) / ( x.iloc[-1]-x.iloc[0]))
    textcoordinates = [ fixed( c) for c in _graph.get_property( 'textcoordinates', [0.05, 0.92])]
    name = lit( '%s' % ( _graph.get_property( 'name', '')))
    if name != '' :
        name = name+': '
    _axes.annotate( '%sb=%s (y=bx)' % ( name, m), xy=( 0.0, 0.0), xycoords='axes fraction', \
        xytext=textcoordinates, textcoords='axes fraction')

    return regression_model
