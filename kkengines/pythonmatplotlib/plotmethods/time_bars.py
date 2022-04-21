
def kkplot_pythonmatplotlib_time_bars( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_time_bars_%s( "%s", _dataframe=%s, _axes=%s)' % ( self._canonicalize_name( _id), _id, dataframe, axes)

    w = self.W.iappendnl
    w( 0, 'def kkplot_plot_time_bars_%s( _id, _dataframe, _axes) :' % ( self._canonicalize_name( _id)))
    w( 1, '_axes.set_gid( _id)')

    w( 1, 'graphlabels = { %s }' % ( self._make_labels( _columns, _graph)))
    w( 1, 'for column in [ %s] :' % ( ','.join([ '"%s"' % c for c in _columns])))
    w( 2, '_axes.bar( _dataframe.index, _dataframe[column].values %s, label=graphlabels[column], gid="%%s" %% ( column))' \
      % ( self._make_args( 'l', \
              zorder=_graph.zorder, \
              color=_graph.get_property( 'color'), \
              edgecolor=_graph.get_property( 'color'), \
              facecolor=_graph.get_property( 'color'))))

    w( 1, '_axes.xaxis_date()')

    return method_call
