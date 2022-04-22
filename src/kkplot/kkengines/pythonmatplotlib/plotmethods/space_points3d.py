
def kkplot_pythonmatplotlib_space_points3d( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_space_points3d_%s( "%s", _dataframe=%s, _axes3d=%s)' % ( self._canonicalize_name( _id), _id, dataframe, axes)

    self.W.iappendnl( 0, 'from mpl_toolkits.mplot3d import Axes3D')
    self.W.iappendnl( 0, 'def kkplot_plot_space_points3d_%s( _id, _dataframe, _axes3d) :' % ( self._canonicalize_name( _id)))
    self.W.iappendnl( 1, '_axes3d.set_gid( _id)')
    self.W.iappendnl( 1, 'for column in [ %s] :' % ( ','.join([ '"%s"' % c for c in _columns])))
    self.W.iappendnl( 2, 'X = _dataframe["x"]')
    self.W.iappendnl( 2, 'Y = _dataframe["y"]')
    self.W.iappendnl( 2, '_axes3d.scatter( X, Y, _dataframe[column], gid="%%s" %% ( column) %s)' \
        % ( self._make_args( 'l', \
                marker=_graph.get_property( "marker", "o"), \
                markersize=_graph.get_property( "markersize"), \
                color=_graph.get_property( "color"), \
                label=_graph.get_property( "label.%s" % ( column)))
        ))

    return method_call

