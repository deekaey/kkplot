
##@page kkplot_pythonmatplotlib_time_raster Raster plot (temporal integration)
#@tableofcontents
#@section option Plotting options
# - agg (mean/sum) Aggregation option for target value

import sys
import numpy
import pandas

from kkplot.kkutils.log import *
from kkplot.kkengines.pythonmatplotlib.helpers import *

def time_raster_columns( _columns, _auxcolumns) :
    columns = _columns + [ c for aux in _auxcolumns for c in aux ]
    xycolumns = find_columns( [ 'x', 'y', 'area'], columns)
    if len( xycolumns) < 2 :
        kklog_error( 'Plot method "raster" requires (x, y) columns')
        return None
    for column in xycolumns[:3 if len( xycolumns) == 3 else 2] :
        columns.remove( column)
    return xycolumns, columns

def _property( _graph, _name, _default) :
    value = _graph.get_property( _name)
    return _default() if value is None else value

def time_raster( _axes, _graph, _data, _columns, _auxcolumns, _ctx) :
    _axes.set_gid( _graph.graphid)
    xycolumns, columns = time_raster_columns( _columns, _auxcolumns)
    X, Y = xycolumns[0], xycolumns[1]
    with_area = len( xycolumns) == 3
    agg = _graph.get_property( 'agg', 'mean')
    data = _data.copy()

    resample = _graph.get_property( 'resample')
    if resample :
        resolution, function = resample.split( '/')[0], resample.split( '/')[1]
        if resolution in [ 'Y', 'YE', 'A'] :
            resolution = 'A' if sys.version_info < ( 3, 9, 4) else 'YE'
        data = getattr( data.groupby( xycolumns[:3] if with_area else xycolumns[:2]).resample( resolution), function)()[columns]
        data = data.reset_index()
        data = data.set_index( pandas.to_datetime( data['time']))
        data.drop( 'time', axis=1, inplace=True)

    if _graph.get_property( 'xoffset') is not None :
        data[X] -= _graph.get_property( 'xoffset')
    if _graph.get_property( 'yoffset') is not None :
        data[Y] -= _graph.get_property( 'yoffset')

    org_mean = data.groupby( [ X, Y]).mean()
    colorbar_kwargs = dict( pad=_graph.get_property( 'colorbarpad'), \
        orientation=_graph.get_property( 'colorbarorientation', 'vertical'))
    cmap = _graph.get_property( 'colormap', 'spectral')

    if not with_area :
        data = data.groupby( [ X, Y]).agg( [ 'sum', 'mean']).reset_index()
        xcolumn, ycolumn = data[X].astype( int), data[Y].astype( int)

        xmin, xmin2, *_ = numpy.partition( numpy.unique( xcolumn), 1)
        ymin, ymin2, *_ = numpy.partition( numpy.unique( ycolumn), 1)
        xcolumn = ( ( xcolumn - numpy.min( xcolumn)) / ( xmin2 - xmin)).astype( int)
        ycolumn = ( ( ycolumn - numpy.min( ycolumn)) / ( ymin2 - ymin)).astype( int)

        xmin, xmax = numpy.min( xcolumn), numpy.max( xcolumn)
        xcolumn -= xmin
        ymin, ymax = numpy.min( ycolumn), numpy.max( ycolumn)
        ycolumn -= ymin
        x_ext, y_ext = xmax-xmin+1, ymax-ymin+1
        sys.stderr.write( 'width/height ratio: %0.4f\n' % ( float( x_ext)/float( y_ext)))

        for column in columns :
            raster = numpy.full( ( y_ext, x_ext), numpy.nan)
            for r, c, v in zip( ycolumn, xcolumn, data[column][agg]) :
                raster[r,c] = v
            c_min = _property( _graph, 'colorbarlimitlow', lambda : numpy.nanmin( raster))
            c_max = _property( _graph, 'colorbarlimithigh', lambda : numpy.nanmax( raster))
            img = _axes.imshow( raster, origin=lit( _graph.get_property( 'origin', 'upper')), vmin=c_min, vmax=c_max, \
                **kwargs( cmap=cmap, interpolation=_graph.get_property( 'interpolation', 'none')))
            colorbar( _axes, img, _graph.labelat( 0, ''), **colorbar_kwargs)
        return

    ## grid cells with different resolution
    A = xycolumns[2]
    org = data.copy( deep=True)
    cbar = None
    for area in numpy.unique( org[A]) :
        data = org.loc[org[A] == area,]
        data = data.groupby( [ X, Y, A]).agg( [ 'sum', 'mean']).reset_index()
        xcolumn, ycolumn = data[X], data[Y]
        resolution = int( area**0.5)

        def grid( _c, _limitlow, _limithigh) :
            limitlow = _property( _graph, _limitlow, lambda : org[_c].min())
            limithigh = _property( _graph, _limithigh, lambda : org[_c].max())
            c_min = data[_c].min() - int( ( data[_c].min()-limitlow)/resolution) * resolution
            c_max = data[_c].max() + int( ( limithigh-data[_c].max())/resolution) * resolution
            return numpy.arange( c_min-1*resolution, c_max+3*resolution, resolution)
        x = grid( X, 'xlimitlow', 'xlimithigh')
        y = grid( Y, 'ylimitlow', 'ylimithigh')

        xv, yv = numpy.meshgrid( x, y)
        data['xmap'] = xcolumn.map( { k: v for v, k in enumerate( x)})
        data['ymap'] = ycolumn.map( { k: v for v, k in enumerate( y)})

        for column in columns :
            raster = numpy.full( ( len( y), len( x)), numpy.nan)
            for r, c, v in zip( data['ymap'], data['xmap'], data[column][agg]) :
                raster[r,c] = v
            c_min = _property( _graph, 'colorbarlimitlow', lambda : org_mean[column].min())
            c_max = _property( _graph, 'colorbarlimithigh', lambda : org_mean[column].max())
            img = _axes.pcolor( xv, yv, raster, vmin=c_min, vmax=c_max, **kwargs( cmap=cmap))
            if cbar is None :
                cbar = colorbar( _axes, img, _graph.labelat( 0, ''), **colorbar_kwargs)
