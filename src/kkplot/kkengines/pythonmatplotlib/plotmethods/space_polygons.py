
def kkplot_pythonmatplotlib_space_polygons( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_space_polygons_%s( "%s", _dataframe=%s, _axes=%s)' \
        % ( self._canonicalize_name( _id), _id, dataframe, axes)

    #kklog_debug( 'polygonsource[%s]=%s' % ( _id, str( _graph.domain.get_property( 'esrishapefile'))))
    #kklog_debug( 'columns=%s' % ( _columns))
    #kklog_debug( 'aux-columns=%s' % ( _auxialiary_columns))

    ## read polygons from ersi shapefile, or ...
    if _graph.domain.get_property( 'esrishapefile') is not None :
        self.W.iappendnl( 0, 'import shapefile')
        self.W.iappendnl( 0, 'def get_polygons_%s( _dataframe) :' % ( self._canonicalize_name( _id)))
        self.W.iappendnl( 1, 'esri = shapefile.Reader( "%s")' % ( str( _graph.domain.get_property( 'esrishapefile'))))
        self.W.iappendnl( 1, 'ids = _dataframe["id"]')
        self.W.iappendnl( 1, 'id_index = %d' % ( int( _graph.domain.get_property( 'esriidindex'))))
        self.W.iappendnl( 1, 'polygons, polygonids = list(), list()')
        self.W.iappendnl( 1, 'value_indexes = numpy.empty( esri.numRecords)')
        self.W.iappendnl( 1, 'for j, element in enumerate( esri.shapeRecords()) :')
        self.W.iappendnl( 2, 'shapeid = element.record[id_index]')
        self.W.iappendnl( 2, 'value_indexes[j] = numpy.where( ids==shapeid)[0] #len( polygons)')
        self.W.iappendnl( 2, 'points = numpy.array( element.shape.points)')
        self.W.iappendnl( 2, 'parts = element.shape.parts')
        self.W.iappendnl( 2, 'polygon_offsets = list( parts) + [ points.shape[0]]')
        self.W.iappendnl( 2, 'for p_ij in range( len( parts)):')
        self.W.iappendnl( 3, 'polygons.append( points[polygon_offsets[p_ij]:polygon_offsets[p_ij+1]])')
        self.W.iappendnl( 3, 'polygonids.append( shapeid)')
        self.W.iappendnl( 1, 'return ( value_indexes, polygons, polygonids)')
        self.W.iappendnl( 0, '')
    elif _graph.domain.get_property( 'grid') is not None :
        self.W.iappendnl( 0, 'def get_polygons_%s( _dataframe) :' % ( self._canonicalize_name( _id)))
        self.W.iappendnl( 1, 'ids = _dataframe["id"]')
        self.W.iappendnl( 1, 'polygons, polygonids = list(), list()')
        self.W.iappendnl( 1, 'x = numpy.round( _dataframe.x, %d)' % ( _graph.domain.get_property( 'xyround', 10)))
        self.W.iappendnl( 1, 'x = x.values')
        self.W.iappendnl( 1, 'y = numpy.round( _dataframe.y, %d)' % ( _graph.domain.get_property( 'xyround', 10)))
        self.W.iappendnl( 1, 'y = y.values')
        self.W.iappendnl( 1, 'w2 = %f/2.0' % ( _graph.domain.get_property( 'xlength', 1.0)))
        self.W.iappendnl( 1, 'h2 = %f/2.0' % ( _graph.domain.get_property( 'ylength', 1.0)))
        self.W.iappendnl( 1, 'polygons = zip( numpy.array( zip(x-w2,y+h2)), numpy.array( zip(x-w2,y-h2)), numpy.array( zip(x+w2,y-h2)), numpy.array( zip(x+w2,y+h2)), numpy.array( zip(x-w2,y+h2)))')
        self.W.iappendnl( 1, 'value_indexes = numpy.array( range( len( _dataframe.id)))')
        self.W.iappendnl( 1, 'return ( value_indexes, polygons, _dataframe.id)')

    else :
        kklog_fatal( 'unknown polygon source')

    self.W.iappendnl( 0, 'from matplotlib.collections import PolyCollection as matplotlib_polycollection')
    self.W.iappendnl( 0, 'from matplotlib import cm as matplotlib_colormaps')
    self.W.iappendnl( 0, 'def kkplot_plot_space_polygons_%s( _id, _dataframe, _axes) :' % ( self._canonicalize_name( _id)))
    self.W.iappendnl( 1, '_axes.set_gid( _id)')

    ## map values to polygons, note that some polygons may comprise several parts
    self.W.iappendnl( 1, 'value_indexes, polygons, polygonids = get_polygons_%s( _dataframe)' % ( self._canonicalize_name( _id)))
    self.W.iappendnl( 1, 'values = pandas.Series( data=[ numpy.nan]*len( polygons))')
    self.W.iappendnl( 1, 'values[value_indexes] = _dataframe["%s"]' % ( _columns[0]))
    self.W.iappendnl( 1, 'values = values.fillna( method="ffill")')

    cmap = self.dviplot.get_property( 'colorscheme')
    cmap = 'Oranges' if cmap is None or cmap != 'grayscale' else 'gray'
    self.W.iappendnl( 1, 'polygon_collection = matplotlib_polycollection( polygons, array=values, cmap=matplotlib_colormaps.%s, closed=True, edgecolors="none", linewidth=None)' \
        % ( _graph.get_property( 'colormap', cmap))) #, linestyle=None)')
    self.W.iappendnl( 1, '_axes.add_collection( polygon_collection)')
    self.W.iappendnl( 1, '_axes.autoscale_view()')
    self.W.iappendnl( 1, 'matplotlib_pyplot.colorbar( polygon_collection, ax=_axes, label=r%s %s)' \
        % ( self._stringify( _graph.labelat( 0, '')), \
            self._make_args( 'l', pad=_graph.get_property( 'colorbarpad'), orientation=_graph.get_property( 'colorbarorientation', 'vertical'))))

    return method_call

