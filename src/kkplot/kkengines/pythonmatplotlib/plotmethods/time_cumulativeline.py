
def kkplot_pythonmatplotlib_time_cumulativeline( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_time_cumulativeline_%s( "%s", _dataframe=%s, _axes=%s)' % ( self._canonicalize_name( _id), _id, dataframe, axes)

    w = self.W.iappendnl
    w( 0, 'def kkplot_plot_time_cumulativeline_%s( _id, _dataframe, _axes) :' % ( self._canonicalize_name( _id)))
    w( 1, '_axes.set_gid( _id)')

    w( 1, 'graphlabels = { %s }' % ( self._make_labels( _columns, _graph)))
    w( 1, 'for column in [ %s] :' % ( ','.join([ '"%s"' % c for c in _columns])))
    w( 2, '_axes.plot( _dataframe.index, _dataframe[column].cumsum().values %s, label=graphlabels[column], gid="%%s" %% ( column))' \
        % ( self._make_args( 'l', \
                zorder=_graph.zorder, \
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


