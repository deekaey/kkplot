
def kkplot_pythonmatplotlib_time_area( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_time_stackedarea_%s( "%s", _dataframe=%s, _axes=%s)' \
        % ( self._canonicalize_name( _id), _id, dataframe, axes)
    columns = [ column for column_1, column_2 in zip( _columns, _auxialiary_columns) for column in [column_1]+column_2]

    w = self.W.iappendnl
    w( 0, 'def kkplot_plot_time_stackedarea_%s( _id, _dataframe, _axes) :' % ( self._canonicalize_name( _id)))
    w( 1, '_axes.set_gid( _id)')

    w( 1, 'columns = [ %s]' % ( ', '.join([ '"%s"' % c for c in columns])))
    w( 1, '_dataframe[columns][_dataframe[columns[0]].notnull()].plot( ax=_axes, kind="area", stacked=True, gid=_id %s)' \
      % ( self._make_args( 'l', \
                zorder=_graph.zorder, \
                color=_graph.get_property( 'color') \
    )))
    w( 1, 'linelabels = { %s }' % ( self._make_labels( columns, _graph)))
    w( 1, 'lines, columnids = _axes.get_legend_handles_labels()')
    w( 1, 'for ( line, cid) in zip( lines, columnids) :')
    w( 2, 'if line.get_label() in linelabels :')
    w( 3, 'line.set_label( linelabels[cid])')

    return method_call


