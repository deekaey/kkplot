
def kkplot_pythonmatplotlib_space_line3d( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_space_line3d_%s( "%s", _dataframe=%s, _axes3d=%s)' % ( self._canonicalize_name( _id), _id, dataframe, axes)

    self.W.iappendnl( 0, 'from mpl_toolkits.mplot3d import Axes3D')
    self.W.iappendnl( 0, 'def kkplot_plot_space_line3d_%s( _id, _dataframe, _axes3d) :' % ( self._canonicalize_name( _id)))
    self.W.iappendnl( 1, '_axes3d.set_gid( _id)')
    self.W.iappendnl( 1, 'X = pandas.DataFrame()')
    self.W.iappendnl( 1, 'X["x"] = _dataframe["x"]')
    self.W.iappendnl( 1, 'Y = pandas.DataFrame()')
    self.W.iappendnl( 1, 'Y["y"] = _dataframe["y"]')
    self.W.iappendnl( 1, 'Z = pandas.DataFrame()')
    self.W.iappendnl( 1, 'Z["z"] = _dataframe["%s"]' % ( _columns[0]))
    self.W.iappendnl( 1, 'for column in [ %s] :' % ( ','.join([ '"%s"' % c for c in _columns[1:]])))
    self.W.iappendnl( 2, 'X["x"][_dataframe["x"].notnull()] = _dataframe["x"][_dataframe["x"].notnull()]')
    self.W.iappendnl( 2, 'Y["y"][_dataframe["y"].notnull()] = _dataframe["y"][_dataframe["y"].notnull()]')
    self.W.iappendnl( 2, 'Z["z"][_dataframe[column].notnull()] = _dataframe[column][_dataframe[column].notnull()]')
    self.W.iappendnl( 1, '_axes3d.plot( X["x"], Y["y"], Z["z"], gid="%%s" %% ( _id) %s)' \
        % ( self._make_args( 'l', \
                marker=_graph.get_property( "marker"), \
                markersize=_graph.get_property( "markersize"), \
                color=_graph.get_property( "color"), \
                label=_graph.get_property( "label.%s" % ( _columns[0])))
        ))

    return method_call

