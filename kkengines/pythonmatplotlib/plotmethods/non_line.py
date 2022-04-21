
from kkutils.log import *

def kkplot_pythonmatplotlib_non_line( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_non_line_%s( "%s", _dataframe=%s, _axes=%s)' % ( self._canonicalize_name( _id), _id, dataframe, axes)

    xcol = _graph.get_property( 'xaxis')

    columns = _columns
    for auxialiary_columns in _auxialiary_columns :
        for auxialiary_column in auxialiary_columns :
            if auxialiary_column.find( '.%s.' % ( xcol)) != -1 or auxialiary_column.endswith( '.%s' % ( xcol)) :
                xcol = auxialiary_column
            else :
                columns += [ auxialiary_column ]

    c_lo, c_hi = ( 0.25, 1)

    w = self.W.iappendnl
    w( 0, 'def kkplot_plot_non_line_%s( _id, _dataframe, _axes) :' % ( self._canonicalize_name( _id)))
    w( 1, '_axes.set_gid( _id)')

    w( 1, 'graphlabels = { %s }' % ( self._make_labels( columns, _graph)))
    w( 1, 'columns = [ %s]' % ( ','.join([ '"%s"' % c for c in columns])))
    w( 1, 'xcol = "%s"' % ( xcol))
    w( 1, 'for j, column in enumerate( columns) :')
    #w( 2, '_dataframe[column].plot( ax=_axes, kind="line" %s, label=graphlabels[column], gid="%%s" %% ( column))' \
    color = ''
    if _graph.get_property( "colormap") :
        w( 2, 'col = %f + ( %f - %f) * float( j)/float( len( columns))' % ( c_lo, c_hi, c_lo))
        color = ', color=matplotlib_colormap.%s( col)' % ( _graph.get_property( "colormap"))
    w( 2, '_axes.plot( _dataframe[xcol].values, _dataframe[column].values %s %s, label=graphlabels[column], gid="%%s" %% ( column))' \
        % ( color, self._make_args( 'l', \
                color=_graph.get_property( 'color'), \
                linestyle=self._get_linestyle( _graph.get_property( 'linestyle', 'solid')), \
                linewidth=_graph.get_property( 'linewidth'), \
                marker=_graph.get_property( 'marker'), \
                markersize=_graph.get_property( 'markersize'), \
                markeredgecolor=_graph.get_property( 'markeredgecolor'), \
                markeredgewidth=_graph.get_property( 'markeredgewidth'), \
                markerfacecolor=_graph.get_property( 'markercolor'), \
                markevery=_graph.get_property( 'markerstride') \
        )))
                #visible=self._toggle( _graph.get_property( 'hidden', False))

    return method_call

