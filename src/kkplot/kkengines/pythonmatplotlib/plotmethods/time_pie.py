
from kkutils.log import *

def kkplot_pythonmatplotlib_time_pie( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_non_pie_%s( "%s", _dataframe=%s, _axes=%s)' % ( self._canonicalize_name( _id), _id, dataframe, axes)

    kklog_debug( 'columns=%s'%(_columns))
    kklog_debug( 'aux-columns=%s'%(_auxialiary_columns))

    columns = _columns
    for auxcolumns in _auxialiary_columns :
        columns += auxcolumns
## TODO  make this a property

    w = self.W.iappendnl
    w( 0, 'def kkplot_plot_non_pie_%s( _id, _dataframe, _axes) :' % ( self._canonicalize_name( _id)))
    w( 1, '_axes.set_gid( _id)')

    w( 1, 'labels = { %s}' % ( self._make_labels( columns, _graph)))
    totalcolumn = columns.pop( 0)
    w( 1, 'totalcolumn = %s' % ( '"%s"' % ( totalcolumn)))
    w( 1, 'columns = [ %s]' % ( ','.join([ '"%s"' % ( column) for column in columns])))
## NOTE total label is labels[totalcolumn]

    w( 1, 'total = _dataframe[totalcolumn].sum()')
    w( 1, 'sys.stderr.write( "total=%f\\n" % ( _dataframe[totalcolumn].sum()))')

    if _graph.get_property( 'unit') is not None :
        w( 1, 'unit = " [%s]"' % ( str( _graph.get_property( 'unit', ''))))
    else :
        w( 1, 'unit = ""')
    w( 1, 'fractions = list()')
    w( 1, 'pielabels = list()')
    w( 1, 'for column in columns :')
    w( 2, 'value = _dataframe[column].sum()')
    w( 2, 'fractions.append( value/total)')
    w( 2, 'pielabels.append( "%s (%0.2f%s)" % ( labels[column], value, unit))')
    w( 2, '#print column, "  f=",fractions[-1], " v=",_dataframe[column].sum()')
    w( 1, 'fractionssum = sum( fractions)')
    w( 1, 'if fractionssum > 1.0 :')
    w( 2, 'sys.stderr.write( "fractions add up to more than 1  [sum of fractions=%f]\\n" % ( fractionssum))')
    w( 1, 'elif fractionssum < 1.0 :')
    w( 2, 'fractions.append( 1.0-fractionssum)')
    w( 2, 'pielabels.append( "? (%.2f)" % ( total*(1.0-fractionssum)))')
    w( 1, 'wedgeexplode = tuple( [0.0]*(len( fractions)-1) + [ 0.05])')

    w( 1, 'colors = matplotlib_colormap.%s( numpy.linspace( 0.2, 0.8, 1+len(columns)))' % ( _graph.get_property( 'colormap', 'PuBu')))

    w( 1, '_axes.pie( fractions, explode=wedgeexplode, labels=pielabels, colors=colors, shadow=True, autopct="%%.2f%%" %s)' \
        % ( self._make_args( 'l', \
                zorder=_graph.zorder \
    )))

    return method_call

