
import sys
from kkutils.log import *

def kkplot_pythonmatplotlib_time_fill( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_time_fill_%s( "%s", _dataframe=%s, _axes=%s)' \
        % ( self._canonicalize_name( _id), _id, dataframe, axes)

    columns = _columns
    for auxialiary_columns in _auxialiary_columns :
        columns += auxialiary_columns

    w = self.W.iappendnl
    w( 0, 'def kkplot_plot_time_fill_%s( _id, _dataframe, _axes) :' % ( self._canonicalize_name( _id)))
    w( 1, '_axes.set_gid( _id)')

    w( 1, 'x = pandas.to_datetime( _dataframe.index)')
    w( 1, 'c1 = _dataframe["%s"]' % ( columns[0]))
    w( 1, 'c2 = _dataframe["%s"]' % ( columns[1]))

    w( 1, '_axes.fill_between( x, c1, c2 %s)' \
        % ( self._make_args( 'l', \
                zorder=_graph.zorder, \
                facecolor=_graph.get_property( 'color'), \
                alpha=_graph.get_property( 'transparency')
        )))

    return method_call

