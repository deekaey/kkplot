
import numpy
from kkplot.kkutils.log import *

def kkplot_pythonmatplotlib_time_raster( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :

    agg_method = _graph.get_property( 'agg', 'mean')

    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_time_raster_%s( "%s", _dataframe=%s, _axes=%s)' % ( self._canonicalize_name( _id), _id, dataframe, axes)

    columns = _columns
    for auxialiary_columns in _auxialiary_columns :
        columns += auxialiary_columns
    kklog_debug( 'columns=%s' % ( columns))

    xycolumns = self._find_columns( [ 'x', 'y', 'area'], columns)
    if len(xycolumns) < 2 :
        kklog_error( 'Plot method "raster" requires (x, y) columns')
        return None

    xcolumn = xycolumns[0]
    columns.remove( xcolumn)
    xcolumn = '_dataframe["%s"]' % ( xcolumn)

    ycolumn = xycolumns[1]
    columns.remove( ycolumn)
    ycolumn = '_dataframe["%s"]' % ( ycolumn)

    indentation = 0
    if len(xycolumns) == 3 :
        indentation += 1
        areacolumn = xycolumns[2]
        columns.remove( areacolumn)
        areacolumn = '_dataframe["%s"]' % ( areacolumn)

    w = self.W.iappendnl

    w( 0, 'def kkplot_plot_time_raster_%s( _id, _dataframe, _axes) :' % ( self._canonicalize_name( _id)))
    w( 1, '_axes.set_gid( _id)')

    w( 1, 'cbar = None')
    w( 1, '_dataframe["%s"] = _dataframe["%s"]-_dataframe["%s"].min()' % ( xycolumns[0], xycolumns[0], xycolumns[0]))
    w( 1, '_dataframe["%s"] = _dataframe["%s"]-_dataframe["%s"].min()' % ( xycolumns[1], xycolumns[1], xycolumns[1]))
    w( 1, 'org_mean = _dataframe.groupby(["%s", "%s"]).mean()' % ( xycolumns[0], xycolumns[1]))
    w( 1, 'org_mean_sum = _dataframe.groupby(["%s", "%s"]).agg(["sum", "mean"])' % ( xycolumns[0], xycolumns[1]))
    if len(xycolumns) == 3 :    
        w( 1, 'org = _dataframe.copy(deep=True)')
        w( 1, 'for area in numpy.unique(org["%s"]):' % ( xycolumns[2]))
        w( 1+indentation, '_dataframe = org.loc[org["%s"] == area,]' % ( xycolumns[2]))
        w( 1+indentation, '_dataframe = _dataframe.groupby(["%s", "%s", "%s"]).agg(["sum", "mean"])' % ( xycolumns[0], xycolumns[1], xycolumns[2]))
    else:
        w( 1+indentation, '_dataframe = _dataframe.groupby(["%s", "%s"]).agg(["sum", "mean"])' % ( xycolumns[0], xycolumns[1]))

    w( 1+indentation, '_dataframe = _dataframe.reset_index()')
    w( 1+indentation, 'graphlabels = { %s }' % ( self._make_labels( columns, _graph, dataframe='_dataframe')))

    w( 1+indentation, 'columns = [ %s]' % ( ','.join([ '"%s"' % c for c in columns])))

    if len(xycolumns) == 3 :    
        w( 1+indentation, 'xcolumn = %s' % ( xcolumn))
        w( 1+indentation, 'ycolumn = %s' % ( ycolumn))
        w( 1+indentation, 'areacolumn = %s\n' % ( areacolumn))
        w( 1+indentation, 'x_coordinates=numpy.unique(xcolumn)')
        w( 1+indentation, 'y_coordinates=numpy.unique(ycolumn)')
        w( 1+indentation, 'resolution=int(area**0.5)')

        w( 1+indentation, 'x_min = _dataframe["%s"].min() -  int((_dataframe["%s"].min()-org["%s"].min())/resolution) * resolution' %(xycolumns[0],xycolumns[0],xycolumns[0]))
        w( 1+indentation, 'x_max = _dataframe["%s"].max() +  int((org["%s"].max()-_dataframe["%s"].max())/resolution) * resolution' %(xycolumns[0],xycolumns[0],xycolumns[0]))
        w( 1+indentation, 'x = numpy.arange(x_min-1*resolution, x_max+3*resolution, resolution)')

        w( 1+indentation, 'y_min = _dataframe["%s"].min() -  int((_dataframe["%s"].min()-org["%s"].min())/resolution) * resolution' %(xycolumns[1],xycolumns[1],xycolumns[1]))
        w( 1+indentation, 'y_max = _dataframe["%s"].max() +  int((org["%s"].max()-_dataframe["%s"].max())/resolution) * resolution' %(xycolumns[1],xycolumns[1],xycolumns[1]))
        w( 1+indentation, 'y = numpy.arange(y_min-1*resolution, y_max+3*resolution, resolution)')

        w( 1+indentation, 'xv, yv = numpy.meshgrid(x,y)')
        w( 1+indentation, 'x_map = {k: v for v, k in enumerate(x)}')
        w( 1+indentation, 'y_map = {k: v for v, k in enumerate(y)}')
        w( 1+indentation, '_dataframe["xmap"] = xcolumn.map( x_map)')
        w( 1+indentation, '_dataframe["ymap"] = ycolumn.map( y_map)')

        w( 1+indentation, 'x_ext, y_ext = len(x), len(y)')
    else:
        w( 1+indentation, 'xcolumn = %s.astype( int)' % ( xcolumn))
        w( 1+indentation, 'ycolumn = %s.astype( int)' % ( ycolumn))

        w( 1+indentation, 'xmin, xmin2, *_ = numpy.partition( numpy.unique(xcolumn), 1)')
        w( 1+indentation, 'ymin, ymin2, *_ = numpy.partition( numpy.unique(ycolumn), 1)')

        w( 1+indentation, 'xcolumn = ((xcolumn - numpy.min( xcolumn)) / (xmin2 - xmin)).astype( int)')
        w( 1+indentation, 'ycolumn = ((ycolumn - numpy.min( ycolumn)) / (ymin2 - ymin)).astype( int)')

        w( 1+indentation, 'xmin, xmax = numpy.min( xcolumn), numpy.max( xcolumn)')
        w( 1+indentation, 'xcolumn -= xmin')
        w( 1+indentation, 'ymin, ymax = numpy.min( ycolumn), numpy.max( ycolumn)')
        w( 1+indentation, 'ycolumn -= ymin')
        w( 1+indentation, 'x_ext, y_ext = xmax-xmin+1, ymax-ymin+1')
        w( 1+indentation, 'sys.stderr.write( "width/height ratio: %0.4f\\n" % ( float(x_ext)/float(y_ext)))')

    w( 1+indentation, 'for j, column in enumerate( columns) :')
    w( 2+indentation, 'raster = numpy.zeros( (y_ext, x_ext))')
    w( 2+indentation, 'raster[:] = numpy.nan')
    
    if len(xycolumns) == 3 :    
        w( 2+indentation, 'for r, c, v in zip( _dataframe["ymap"], _dataframe["xmap"], _dataframe[column]["%s"]) :' %agg_method)
    else :
        w( 2+indentation, 'for r, c, v in zip( ycolumn, xcolumn, _dataframe[column]["%s"]) :' %agg_method)
    w( 3+indentation, 'raster[r,c] = v')

    # imshow options:  aspect="auto"
    w( 2+indentation, '#img = _axes.tripcolor( xcolumn,ycolumn, _dataframe[column]["%s"])' %agg_method)

    if len(xycolumns) == 3 :    
        w( 2+indentation, 'c_min=%s' % ( _graph.get_property( 'colorbarlimitlow', 'org_mean[column].min()')))
        w( 2+indentation, 'c_max=%s' % ( _graph.get_property( 'colorbarlimithigh', 'org_mean[column].max()')))
        w( 2+indentation, 'img = _axes.pcolor( xv-0.5*resolution, yv-0.5*resolution, raster, vmin=c_min, vmax=c_max %s)' \
            % ( self._make_args( 'l', \
                cmap=_graph.get_property( 'colormap', 'spectral') \
            )))

        w( 2+indentation, 'if cbar == None:')
        w( 3+indentation, 'cbar = matplotlib_pyplot.colorbar( img, ax=_axes, label=%s %s)' \
            % ( self._stringify( _graph.labelat( 0, '')), \
                self._make_args( 'l', \
                    pad=_graph.get_property( 'colorbarpad'),
                    orientation=_graph.get_property( 'colorbarorientation', 'vertical')
            )))
    else:
        w( 2+indentation, 'c_min=%s' % ( _graph.get_property( 'colorbarlimitlow', 'numpy.nanmin( raster)')))
        w( 2+indentation, 'c_max=%s' % ( _graph.get_property( 'colorbarlimithigh', 'numpy.nanmax( raster)')))
        w( 2+indentation, 'origin="%s"' % ( _graph.get_property( 'origin', 'upper')))
        w( 2+indentation, 'img = _axes.imshow( raster, origin=origin, vmin=c_min, vmax=c_max %s)' \
            % ( self._make_args( 'l', \
                cmap=_graph.get_property( 'colormap', 'spectral'), \
                interpolation=_graph.get_property( 'interpolation', 'none') \
            )))
        w( 2+indentation, 'cbar = matplotlib_pyplot.colorbar( img, ax=_axes, label=%s %s)' \
            % ( self._stringify( _graph.labelat( 0, '')), \
                self._make_args( 'l', \
                    pad=_graph.get_property( 'colorbarpad'),
                    orientation=_graph.get_property( 'colorbarorientation', 'vertical')
            )))

    #if _graph.get_property( "colormap") :
    #color = ', color=matplotlib_colormap.%s( col)' % ( _graph.get_property( "colormap"))
#    w( 2, '_axes.plot( %s, %s %s %s, label=graphlabels[column], gid="%%s" %% ( column))' \
#        % ( xcolumn, ycolumn, color, self._make_args( 'l', \
#                zorder=_graph.zorder, \
#                color=_graph.get_property( 'color'), \
#                linestyle=self._get_linestyle( _graph.get_property( 'linestyle', 'solid')), \
#                linewidth=_graph.get_property( 'linewidth'), \
#                marker=_graph.get_property( 'marker'), \
#                markersize=_graph.get_property( 'markersize'), \
#                markeredgecolor=_graph.get_property( 'markeredgecolor'), \
#                markeredgewidth=_graph.get_property( 'markeredgewidth'), \
#                markerfacecolor=_graph.get_property( 'markercolor'), \
#                markevery=_graph.get_property( 'markerstride') \
#        )))

    return method_call

