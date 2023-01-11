
def kkplot_pythonmatplotlib_time_heatmap( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_time_heatmap_%s( "%s", _dataframe=%s, _axes=%s)' \
        % ( self._canonicalize_name( _id), _id, dataframe, axes)

    auxialiary_columns = [ cols[0] for cols in _auxialiary_columns]

    w = self.W.iappendnl
    w( 0, 'from matplotlib import cm as matplotlib_colormaps')
    w( 0, 'def kkplot_plot_time_heatmap_%s( _id, _dataframe, _axes) :' \
        % ( self._canonicalize_name( _id)))
    w( 1, '_axes.set_gid( _id)')

    w( 1, 'columns = [ %s]' % ( ','.join([ '"%s"' % c for c in _columns])))
    w( 1, 'dataframe = _dataframe[columns][_dataframe[columns[0]].notnull()]')
    w( 1, 'c = numpy.array( dataframe.T.values)')
    w( 1, 'c_min, c_max = %s, %s'
        % ( _graph.get_property( 'colorbarlimitlow', 'numpy.nanmin( c)'),
            _graph.get_property( 'colorbarlimithigh', 'numpy.nanmax( c)')))
    w( 1, 'if numpy.isnan( c_min) or numpy.isnan( c_max) :')
    w( 2, 'print( "[WW] no valid data for graph; ignoring")')
    w( 1, 'else :')
    w( 2, 'x = dataframe.index')#matplotlib_dates.drange( dataframe.index.min(), dataframe.index.max()+datetime.timedelta( days=1), datetime.timedelta( days=1))')
    #w( 2, 'x = matplotlib_dates.drange( dataframe.index.min(), dataframe.index.max()+datetime.timedelta( days=1), datetime.timedelta( days=1))')
    w( 2, 'levels = _dataframe[[%s]]' % ( ','.join([ '"%s"' % c for c in auxialiary_columns])))
    w( 2, 'y = numpy.array( levels.loc[levels.first_valid_index()].T.values)')
        
    #hack in order to allow for plots including nan-values
    w( 2, 'delete = []')
    w( 2, 'for del_i in range( len( y)) :')
    w( 3, 'if numpy.isnan( y[del_i]) :')
    w( 4, 'delete.append( del_i)')
    w( 2, 'y = numpy.delete(y, delete)')
    w( 2, 'c = numpy.delete(c, delete, axis=0)')

    w( 2, "#print 'x=',x.shape,  ' y=',y.shape, ' c=',c.shape")

    cmap = self.dviplot.get_property( 'colorscheme')
    cmap = 'Oranges' if cmap is None or cmap != 'grayscale' else 'gray'
    w( 2, 'kkheatmap = _axes.pcolormesh( x, y, c, cmap=matplotlib_colormaps.%s, vmin=c_min, vmax=c_max %s)' \
        % ( _graph.get_property( 'colormap', cmap), \
            self._make_args( 'l', 
                shading=_graph.get_property( 'shading', 'flat'),
                zorder=_graph.zorder 
        )))
    w( 2, 'cbar = matplotlib_pyplot.colorbar( kkheatmap, ax=_axes, label=r%s %s)' \
        % ( self._stringify( _graph.get_property( 'colorbarlabel', _graph.labelat( 0, ''))), \
            self._make_args( 'l',
                pad=_graph.get_property( 'colorbarpad'),
                orientation=_graph.get_property( 'colorbarorientation', 'horizontal')
    )))
    w( 2, 'annotation = "%s"' %_graph.get_property( 'annotate', 'None')) 
    w( 2, 'if annotation != "None":')
    w( 3, 'for Xi, X in enumerate(x):')
    w( 4, 'for Yi, Y in enumerate(y):')
    w( 5, 'if not numpy.isnan(c[Yi][Xi]):')
    w( 6, '_axes.plot(X, Y, annotation, markerfacecolor="none", color="black")')
    w( 2, '_axes.xaxis_date()')

    return method_call

