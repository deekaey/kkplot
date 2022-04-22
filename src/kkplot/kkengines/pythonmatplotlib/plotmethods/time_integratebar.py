from kkplot.kkutils.log import *

##@page time_integratebar Bar plot (temporal integration)
#@tableofcontents
#@section option Plotting options
# - errors
# - xpositions
# - time_period
# - op
def kkplot_pythonmatplotlib_time_integratebar( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :

    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_time_integratebar_%s( "%s", _dataframe=%s, _axes=%s)' \
        % ( self._canonicalize_name( _id), _id, dataframe, axes)

    kklog_debug( _columns)
    #kklog_debug( '#groups=%d' % ( len(_auxialiary_columns)))
    kklog_debug( _auxialiary_columns)
    n_groups = 1+len( _auxialiary_columns[0])
    n_selects = len( _auxialiary_columns)
    w = self.W.iappendnl
 
    w( 0, 'from scipy import integrate')
    w( 0, 'def kkplot_plot_time_integratebar_%s( _id, _dataframe, _axes) :' \
        % ( self._canonicalize_name( _id)))
    w( 1, '_axes.set_gid( _id)')
    timeresolution = _graph.get_property( "timeresolution", "day")
    w( 1, 'error_columns = %s' % _graph.get_property( "errors", None))
    w( 1, 'xpositions = %s' % _graph.get_property( "xpositions", None))
    w( 1, 'time_period = %f ##resolution is %s' % ( _graph.domain.time_period( timeresolution), timeresolution))
    w( 1, 'aggregated = numpy.zeros( ( %d, %d))' % ( n_selects, n_groups))
    w( 1, 'errors = numpy.zeros( ( %d, %d))' % ( n_selects, n_groups))
    w( 1, 'columns = [ %s]' % ( ','.join([ '"%s"' % ( column) for column in _columns])))
    w( 1, 'auxcolumns = [ %s]' % ( ','.join([ '[%s]' % ( ','.join( [ '"%s"' % c for c in auxcolumn])) for auxcolumn in _auxialiary_columns])))

    w( 1, 'for ( k, ( sel, groups)) in enumerate( zip( %s, %s)) :' % ( 'columns', 'auxcolumns'))

    w( 2, 'graph_operation = "%s"' % ( _graph.get_property( 'op', 'sum')))
    
    w( 2, 'if graph_operation == "mean":')
    w( 3, 'for ( l, group) in enumerate( [sel]+groups) :')
    w( 4, 'data_clean = _dataframe[group].dropna()')
    w( 4, 'aggregated[k,l] = data_clean.mean()')
    w( 4, 'errors[k,l] = data_clean.mean()')

    w( 2, 'elif graph_operation == "sum":')
    w( 3, 'for ( l, group) in enumerate( [sel]+groups) :')
    w( 4, 'data_clean = _dataframe[group].dropna()')
    w( 4, 'aggregated[k,l] = data_clean.sum()')
    w( 4, 'errors[k,l] = data_clean.sum()')

    w( 2, 'elif graph_operation == "integrate":')
    w( 3, 'for ( l, group) in enumerate( [sel]+groups) :')
    w( 4, 'data_clean = _dataframe[group].dropna()')
    w( 4, 'x = [0.0]')
    w( 4, 'for d in range(len(data_clean.index)-1):')
    w( 5, 'x.append( (data_clean.index[d+1]-data_clean.index[d]).total_seconds() + x[d])')
    w( 4, 'aggregated[k,l] = integrate.trapz(data_clean, x) / (data_clean.index[-1]-data_clean.index[0]).total_seconds() * time_period')
    w( 4, 'errors[k,l] = (integrate.trapz(data_clean**2.0, x) / (data_clean.index[-1]-data_clean.index[0]).total_seconds())**0.5 * time_period')

    graphlabels = ','.join( ([ '""' if _graph.label(name) is None else '"%s"' % ( _graph.label(name)) for name in _graph.NAMES]))
    columnnames = ','.join( ([ '"%s"' % name for name in _graph.NAMES]))

    w( 1, 'graphlabels = [ %s ]' % graphlabels)
    w( 1, 'columnnames = [ %s ]' % columnnames)
    w( 1, 'Aggregated = pandas.DataFrame( aggregated, columns=graphlabels)')
    w( 1, 'Errors = pandas.DataFrame( errors, columns=columnnames)')

    add_arguments =  ( self._make_args( 'l', \
                zorder=_graph.zorder, \
                capsize=_graph.get_property( 'capsize', 0.0) , \
                width=_graph.get_property( 'barwidth', 0.5), \
                color=_graph.get_property( 'color', None)
                ))

    add_label = ''

    w( 1, 'if len(Aggregated) > 1:')
    w( 2, 'Aggregated.plot( ax=_axes, kind="bar" %s)' % add_arguments)
    
    w( 1, 'elif error_columns:')
    w( 2, 'for e in range(len(error_columns)):')
    w( 3, 'error_columns[e] = error_columns[e]-1')
    w( 2, 'errorbars = Errors[Errors.columns[error_columns]]')
    w( 2, 'Aggregated = Aggregated.drop(Aggregated.columns[error_columns],  axis=1)')
    w( 2, 'if xpositions == None: ')
    w( 3, 'xpositions = range(len(list(Aggregated.iloc[0]))) ')    
    w( 2, 'for v in range(len(xpositions)):')    
    w( 3, '_axes.bar( xpositions[v], '
                    +'Aggregated.iloc[0,v], ' 
                    +'label=graphlabels[v], '
                    +'yerr=errorbars.iloc[0,v] %s)' % add_arguments)

    w( 1, 'else:')
    w( 2, 'if xpositions == None: ')
    w( 3, 'xpositions = range(len(list(Aggregated.iloc[0]))) ')       
    w( 2, '_axes.bar( xpositions,'
                    +'list(Aggregated.iloc[0]) %s)' % add_arguments)
    
    w( 1, '_axes.set_xticklabels( [ %s], rotation="horizontal")' % ( ','.join([ '"%s"' % ( _graph.datalabel( dataselect)) for dataselect in _graph])))
    w( 0, '')
    w( 1, 'return Aggregated')

    return method_call

