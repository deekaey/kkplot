
def kkplot_pythonmatplotlib_time_boxes( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_time_boxes_%s( "%s", _dataframe=%s, _axes=%s)' \
        % ( self._canonicalize_name( _id), _id, dataframe, axes)

    columns = _columns
    for auxialiary_columns in _auxialiary_columns :
        columns += auxialiary_columns

    w = self.W.iappendnl
    w( 0, 'def kkplot_plot_time_boxes_%s( _id, _dataframe, _axes) :' % ( self._canonicalize_name( _id)))
    w( 1, '_axes.set_gid( _id)')

    w( 1, 'graphlabels = { %s }' % ( self._make_labels( columns, _graph)))
    #w( 1, 'for column in [ %s] :' % ( ','.join([ '"%s"' % c for c in columns])))
    w( 1, 'columns = [ %s]' % ( ','.join([ '"%s"' % c for c in columns])))
    #w( 1, '_dataframe.plot( kind="box", ax=_axes, vert=False, column=columns, return_type="axes", labels=[ "%s" % graphlabels[lbl] for lbl in columns ])')
    w( 1, 'boxes = _axes.boxplot( vert=False, x=_dataframe[columns].values %s, labels=[ "%s" % graphlabels[lbl] for lbl in columns ], medianprops=dict(color="black"))' \
      % ( self._make_args( 'l', \
                zorder=_graph.zorder \
    )))

    boxcolors = None
    if _graph.get_property( 'color') is None :
        pass
    if isinstance( _graph.get_property( 'color'), list) :
    	boxcolors = _graph.get_property( 'color')
    else :
        boxcolors = [ _graph.get_property( 'color') ] * len( columns)

    if boxcolors :
        w( 1, 'for j, box in enumerate( boxes["boxes"]) :')
        w( 2, 'matplotlib.pyplot.setp( box, color=[%s][j])' % ( ','.join([ '"%s"' % c for c in boxcolors])))

    #w( 1, 'matplotlib.pyplot.tick_params( axis="x", which="both", bottom="off", top="off", labelbottom="off")')
    #w( 1, 'matplotlib.pyplot.tick_params( axis="y", which="both", bottom="off", top="off", labelbottom="off")')
    w( 1, '_axes.set_xticks( [])')
    w( 1, '_axes.set_yticks( [])')

    #w( 1, '_axes.yaxis.set_ticklabels( [ "%s" % graphlabels[lbl] for lbl in columns ])')
    #w( 1, '_axes.set_aspect( 2.5)')

    return method_call

