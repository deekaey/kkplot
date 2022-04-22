
from kkutils.log import *

def kkplot_pythonmatplotlib_time_scatter( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_time_scatter_%s( "%s", _dataframe=%s, _axes=%s)' \
        % ( self._canonicalize_name( _id), _id, dataframe, axes)

    columns = _columns
    for auxialiary_columns in _auxialiary_columns :
        columns += auxialiary_columns
    kklog_debug( 'columns=%s' % ( columns))

    xycolumns = self._find_columns( [ 'x', 'y'], columns)
    if len(xycolumns) != 2 :
        kklog_error( 'Plot method "scatter" requires (x, y) columns')
        return None
    xcolumn = xycolumns[0]
#    columns.remove( xcolumn)
    xcolumn = '_dataframe["%s"]' % ( xcolumn)
    ycolumn = xycolumns[1]
#    columns.remove( ycolumn)
    ycolumn = '_dataframe["%s"]' % ( ycolumn)

    w = self.W.iappendnl

    w( 0, 'def kkplot_plot_time_scatter_%s( _id, _dataframe, _axes) :' % ( self._canonicalize_name( _id)))
    w( 1, '_axes.set_gid( _id)')

#    w( 1, 'columns = [ %s]' % ( ','.join([ '"%s"' % c for c in columns])))

    w( 1, 'xcolumn = %s' % ( xcolumn))
    w( 1, 'ycolumn = %s' % ( ycolumn))

#    w( 1, 'graphlabel = "%s"' % ( _graph.labelat( 0)))
    w( 1, '_axes.scatter( xcolumn, ycolumn %s)'
        % ( self._make_args( 'l', \
                color=_graph.get_property( 'color'), \
                linewidth=_graph.get_property( 'linewidth'), \
                marker=_graph.get_property( 'marker'), \
                markersize=_graph.get_property( 'markersize'), \
                markeredgecolor=_graph.get_property( 'markeredgecolor'), \
                markeredgewidth=_graph.get_property( 'markeredgewidth'), \
                markerfacecolor=_graph.get_property( 'markercolor'), \
                markevery=_graph.get_property( 'markerstride'), \
                zorder=_graph.zorder, \
                label=_graph.labelat( 0) \
        )))
#    w( 1, 'x0, x1 = _axes.get_xlim()')
#    w( 1, 'y0, y1 = _axes.get_ylim()')
#    w( 1, '_axes.set_aspect( abs( x1-x0) / abs( y1-y0))')
 
    return method_call

