
def kkplot_pythonmatplotlib_space_boxes( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_space_boxes_%s( "%s", _dataframe=%s, _axes=%s)' \
        % ( self._canonicalize_name( _id), _id, dataframe, axes)

    w = self.W.iappendnl
    w( 0, 'def kkplot_plot_space_boxes_%s( _id, _dataframe, _axes) :' % ( self._canonicalize_name( _id)))
    w( 1, '_axes.set_gid( _id)')

    w( 1, 'graphlabels = { %s }' % ( self._make_labels( _columns, _graph)))
    #w( 1, 'for column in [ %s] :' % ( ','.join([ '"%s"' % c for c in _columns])))
    w( 1, 'columns = [ %s]' % ( ','.join([ '"%s"' % c for c in _columns])))
    w( 1, '_dataframe.boxplot( ax=_axes, column=columns, return_type="axes")')
    w( 1, '_axes.xaxis.set_ticklabels( [ "%s" % graphlabels[lbl] for lbl in columns ])')
    #w( 1, '_axes.set_aspect( 2.5)')

    return method_call

