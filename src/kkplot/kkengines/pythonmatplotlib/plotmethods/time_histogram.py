
def kkplot_pythonmatplotlib_time_histogram( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_time_histogram_%s( "%s", _dataframe=%s, _axes=%s)' \
        % ( self._canonicalize_name( _id), _id, dataframe, axes)

    w = self.W.iappendnl
    w( 0, 'def kkplot_plot_time_histogram_%s( _id, _dataframe, _axes) :' \
        % ( self._canonicalize_name( _id)))
    w( 1, '_axes.set_gid( _id)')

    if len( _columns) > 1 :
        w( 1, 'alpha = 0.7')
    else :
        w( 1, 'alpha = 1.0')
    w( 1, 'columns = [ %s]' % ( ','.join([ '"%s"' % c for c in _columns])))
    w( 1, 'rmin, rmax = min(_dataframe[columns].min( skipna=True)), max(_dataframe[columns].max( skipna=True))')
    w( 1, 'for column in columns :')
    w( 2, 'n_bins = %d' % ( int( _graph.get_property( 'bins', 10))))
    w( 2, '_dataframe[column].hist( ax=_axes, bins=n_bins, range=( rmin, rmax) %s, alpha=alpha, label="_%%s" %% ( column), gid="%%s" %% ( column))' \
        % ( self._make_args( 'l', \
                color=_graph.get_property( 'color'), \
                zorder=_graph.zorder \
    )))

    return method_call

