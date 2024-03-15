
def kkplot_pythonmatplotlib_time_points_errors( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_time_points_errors_%s( "%s", _dataframe=%s, _axes=%s)' % ( self._canonicalize_name( _id), _id, dataframe, axes)
    auxialiary_columns = [ cols[0] for cols in _auxialiary_columns]

    w = self.W.iappendnl
    w( 0, 'def kkplot_plot_time_points_errors_%s( _id, _dataframe, _axes) :' % ( self._canonicalize_name( _id)))
    w( 1, '_axes.set_gid( _id)')

    w( 1, 'graphlabels = { %s }' % ( self._make_labels( _columns, _graph)))
    w( 1, 'for ( data, yerr) in zip( [ %s], [ %s]) :' \
        % ( ','.join([ '"%s"' % c for c in _columns]), ','.join([ '"%s"' % c for c in auxialiary_columns])))
    w( 2, '_axes.errorbar( _dataframe.index.values, _dataframe[data].values, yerr=_dataframe[yerr] %s, label=graphlabels[data], gid="%%s" %% ( data))' \
        % ( self._make_args( 'l', \
                zorder=_graph.zorder, \
				capsize=_graph.get_property( 'capsize', None), \
                color=_graph.get_property( 'color'), \
                linestyle=self._get_linestyle( _graph.get_property( 'linestyle', 'solid')), \
                linewidth=_graph.get_property( 'linewidth', 0.0), \
                elinewidth=_graph.get_property( 'elinewidth', 1.0), \
                marker=_graph.get_property( 'marker', '.'), \
                markersize=_graph.get_property( 'markersize'), \
                markeredgecolor=_graph.get_property( 'markeredgecolor'), \
                markeredgewidth=_graph.get_property( 'markeredgewidth'), \
                markerfacecolor=_graph.get_property( 'markercolor'), \
                markevery=_graph.get_property( 'markerstride') \
            )))
                #visible=self._toggle( _graph.get_property( 'hidden', False))

    return method_call

