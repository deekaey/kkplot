
from kkutils.log import *

def kkplot_pythonmatplotlib_space_surface3d( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_space_surface3d_%s( "%s", _dataframe=%s, _axes=%s)' % ( self._canonicalize_name( _id), _id, dataframe, axes)

    kklog_debug( 'columns=%s'%(_columns))
    kklog_debug( 'aux-columns=%s'%(_auxialiary_columns))

    gridsize = _graph.get_property( 'gridsize', None)
    if gridsize is None :
        return None
    gridsize_x, gridsize_y = tuple( gridsize)

    columns = _columns
    for auxcolumns in _auxialiary_columns :
        columns += auxcolumns

    w = self.W.iappendnl
    w( 0, 'from matplotlib import cm as matplotlib_colormaps')
    w( 0, 'def kkplot_plot_space_surface3d_%s( _id, _dataframe, _axes) :' % ( self._canonicalize_name( _id)))
    w( 1, '_axes.set_gid( _id)')

    w( 1, 'labels = { %s}' % ( self._make_labels( columns, _graph)))
    w( 1, 'columns = [ %s]' % ( ','.join([ '"%s"' % ( column) for column in columns])))

    w( 1, 'rmin, rmax = min(_dataframe[columns].min( skipna=True)), max(_dataframe[columns].max( skipna=True))')
    w( 1, 'for column in columns :')
#    w( 2, 'if numpy.isnan( c_min) or numpy.isnan( c_max) :')
#    w( 2, '    print( "[WW] no valid data for graph; ignoring")')
#    w( 2, 'else :')
    w( 2, 'Z = numpy.array( _dataframe["z"].T.values+_dataframe[column].values).reshape(( %d,%d))' \
        % ( gridsize_x, gridsize_y))
    #w( 3, 'z_min, z_max = numpy.nanmin( c), numpy.nanmax( c)')
    w( 2, 'X, Y = numpy.array( _dataframe["x"].values).reshape(( %d,%d)), numpy.array( _dataframe["y"].values).reshape(( %d,%d))' \
        % ( gridsize_x, gridsize_y, gridsize_x, gridsize_y))

    w( 2, 'surface3d = _axes.plot_surface( X, Y, Z, rstride=1, cstride=1, cmap=matplotlib_colormaps.%s %s)' \
        % ( _graph.get_property( 'colormap', 'RdBu'), \
        self._make_args( 'l', vmin=_graph.get_property( 'zlimitlow'), vmax=_graph.get_property( 'zlimithigh'))))
    w( 2, 'cbar = matplotlib_pyplot.colorbar( surface3d, ax=_axes, label=labels[column])')

    #w( 3, '_axes.set_zlim3d( z_min, z_max)')
    w( 1, '_axes.axis( "tight")')

    return method_call

