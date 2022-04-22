
from kkplot.kkutils.log import *
from kkplot.kkutils import esri as shapefile
from PIL import Image, ImageDraw
import numpy as numpy
import random as random
from scipy import interpolate

def kkplot_pythonvtk_time_surface( self, _id, _graph, _columns, _auxialiary_columns, **_kwargs) :
    w = self.writer.iappendnl

##    kklog_debug( '%s' % ( _graph))

    graphid = self._canonicalize_name( _id)
    dataframe = _kwargs['dataframe']
    outputdir = _kwargs['outputdir']

    columns = _columns
    for auxialiary_columns in _auxialiary_columns :
        columns += auxialiary_columns

    extents = _graph.get_kindproperty( 'extents')
    if extents is None :
        kklog_error( 'plot method requires kind property "extents" { (X,Y), ESRI ShapeFile } [graph=%s]' % graphid)
        return None

    w( 0, 'def kkplot_plot_time_surface_%s( _id, _dataframe) :' % ( graphid))

    w( 1, 'graphlabels = { %s }' % ( self._make_labels( columns, _graph)))


    rc_grid = 0
    if  isinstance( extents, str) and len( extents) > 0 :
        w( 1, 'vtk_filename = "%s/%s.%%04d.vts"' % ( outputdir, graphid))
        rc_grid = kkplot_pythonvtk_time_surface_esri(
            self, _graph, columns, extents, dataframe, _kwargs)
    else :
        kklog_error( 'plot method\'s kind property "extents" has unsupported type  [%s]' % ( type( extents)))
        self.writer.set_error()
        return None

    if rc_grid :
        self.writer.set_error()
        return None


#    w( 2, 'vtk_writer.SetFileName( "%%s/%s.%%s-%%04d%%02d%%02d-%%02d%%02d.vtr" %% ( outputdir, columnname, T.year,T.month,T.day,T.hour,T.minute))' % ( graphid))
#    w( 2, 'vtk_writer.SetFileName( "%%s/%s.%%s-%%04d.vtr" %% ( outputdir, columnname, t))' % ( graphid))
    w( 2, 'vtk_writer.SetFileName( vtk_filename % ( t))')
    w( 2, 'if vtk.VTK_MAJOR_VERSION <= 5:')
    w( 3, 'vtk_writer.SetInput( vtk_grid)')
    w( 2, 'else:')
    w( 3, 'vtk_writer.SetInputData( vtk_grid)')
    w( 2, 'vtk_writer.Write()')
    if _graph.get_kindproperty( 'collection', False) :
        ## TODO  write collection
        pass


    method_call = 'kkplot_plot_time_surface_%s( "%s", _dataframe=%s)' \
         % ( graphid, _id, dataframe)
    return  method_call

def kkplot_pythonvtk_time_surface_esri( self, _graph, _columns, _extents, _dataframe, _kwargs) :
    w = self.writer.iappendnl

    meta_columns = list()
    id_column = None
    for column in _columns :
        if column.endswith( '.id') :
            id_column = column
            meta_columns.append( id_column)
    kklog_debug( 'id-column=%s' % id_column)

    value_columns = list()
    for column in _columns :
        if column not in meta_columns :
            value_columns.append( column)
    columns = value_columns

    ugrid = shapefile.Reader( '%s' % ( _extents))

    id_field = None
    id_field_name = _graph.get_kindproperty( 'idfield', 'ID')
    elevation_field = None
    elevation_field_name = _graph.get_kindproperty( 'elevationfield', 'elevation')
    j = 0
    for f_j in ugrid.fields :
        if isinstance( f_j, tuple) :
            continue
        kklog_debug( 'field[%d]=\n%s [%s]' % ( j, f_j, ugrid.fields[j]))
        if f_j[0] == id_field_name :
            id_field = j
        if f_j[0] == elevation_field_name :
            elevation_field = j

        j += 1
    if id_field is None :
        kklog_error( 'unable to find "Cell ID" field; maybe provide mapping via kind property "idfield"')
        return -1
    if elevation_field is None :
        kklog_error( 'unable to find "Elevation" field; maybe provide mapping via kind property "elevationfield"')
        return -1

    n_cells = len( ugrid.shapes())


    rasterextents = _graph.get_kindproperty( 'rasterextents')
    if rasterextents is None or len( rasterextents) != 2 :
        kklog_error( 'invalid raster extents. provide (n_x, n_y) tuple via "rasterextents"')
        return -1
## NOTE  we reset K according to ratio of bounding box
    J, K = rasterextents[0], rasterextents[1]

    bbox = ugrid.bbox
    X, Y = bbox[2]-bbox[0], bbox[3]-bbox[1]
    K = int( J * ( Y / X))
    kklog_debug( '#shapes=%d, J=%0.2f, K=%0.2f, X=%0.2f, Y=%.02f' % ( n_cells, J, K, X, Y))
    #for j, s_j in enumerate( ugrid.iterShapeRecords()) :
    #    print( '%d\t%s' % ( s_j.record[id_field], s_j.record[elevation_field]))
    #exit()

    raster = Image.new( 'RGB', ( J, K), '#ffffff')

    C_x = lambda j : j*X/float(J)
    C_y = lambda k : k*Y/float(K)
    C_j = lambda x : x*float(J)/X
    C_k = lambda y : y*float(K)/Y

    E_id = dict()
    id_to_rgb = lambda cid : '#%06x' % ( cid)
    for j, s_j in enumerate( ugrid.iterShapeRecords()) :
        n_points = len( s_j.shape.points)

        cellid = s_j.record[id_field]

        elevation = s_j.record[elevation_field]
        E_id[cellid] = elevation

        vertices = list()
        for r, p_k in enumerate( s_j.shape.points) :
            x, y = p_k[0]-bbox[0], p_k[1]-bbox[1]
            j = C_j( x)
            k = C_k( y)
            vertices.append( ( j, k))
        ImageDraw.Draw( raster).polygon( vertices, id_to_rgb(cellid), id_to_rgb(cellid))

    id_raster = numpy.array( raster)
    id_raster = numpy.array( list(map( lambda C : numpy.array([ c[0]*256*256+c[1]*256+c[2] for c in C]), id_raster)))

    INVALID_ID = 256**3-1

    P = dict()
    E = dict()
    for k, col in enumerate( id_raster) :
        for j, row in enumerate( col) :
            cid = col[j]
            if cid != INVALID_ID :
                if cid not in P :
                    P[cid] = list()
                P[cid].append((j,k))
                E[(j,k)] = float( E_id[cid])

## sk:surface    E_k, E_j = numpy.where( id_raster!=INVALID_ID)
## sk:surface
## sk:surface    n_S = 300
## sk:surface    S = random.sample( range( len( E_j)), min( len( E_j), n_S))
## sk:surface    S.sort()
## sk:surface    S = [ (E_j[l], E_k[l]) for l in S ]
## sk:surface    S_x = numpy.array( [ C_x(j) for (j, k) in S ])
## sk:surface    S_y = numpy.array( [ C_y(k) for (j, k) in S ])
## sk:surface    S_z = numpy.array( [ E[(j,k)] for (j, k) in S ])

## sk:interp2d    E_min, E_max = min( E.values()), max( E.values())
## sk:interp2d    print E_min, E_max
## sk:interp2d    exit()
## sk:interp2d    I_z = interpolate.interp2d( S_x, S_y, S_z, kind='cubic')
## sk:interp2d    for ( j, k) in zip( E_j, E_k) :
## sk:interp2d        z = I_z( C_x(j), C_y(k))[0]
## sk:interp2d        if z > E_max :
## sk:interp2d            z = E_max
## sk:interp2d        if z < E_min :
## sk:interp2d            z = E_min
## sk:interp2d        E[(j,k)] = z

## sk:griddata    X_i, Y_i = list(), list()
## sk:griddata    for r, ( j, k) in enumerate( zip( E_j, E_k)) :
## sk:griddata        X_i.append( C_x(j))
## sk:griddata        Y_i.append( C_y(k))
## sk:griddata    X_i, Y_i = numpy.meshgrid( numpy.array(X_i), numpy.array(Y_i))
## sk:griddata    I_z = interpolate.griddata(( S_x, S_y), S_z, ( X_i, Y_i), method='linear')
## sk:griddata    for ( j, k) in zip( E_j, E_k) :
## sk:griddata        E[(j,k)] = E_min if numpy.isnan( I_z[j,k]) else I_z[j,k]

    w( 1, 'P = %s' % ( P))
    w( 1, 'E = %s' % ( E))
    w( 1, 'E_min, E_max = min( E.values()), max( E.values())')

    ## define grid
    w( 1, 'J, K, L = ( %d, %d, %d)' % ( J, K, 1))
    w( 1, 'vtk_grid = vtk.vtkStructuredGrid()')
    w( 1, 'vtk_grid.SetDimensions( J, K, L)')
    w( 1, 'vtk_points = vtk.vtkPoints()')
    w( 1, 'vtk_points.SetNumberOfPoints( J*K*L)')
    w( 1, 'for j in range( J) :')
    w( 2, 'for k in range( K) :')
    w( 3, 'for l in range( L) :')
    w( 4, 'x,y,z = j*%f, k*%f, l*%f' % ( X/float(J), Y/float(K), 0.0))
    w( 4, 'z = E[( j,k)] if ( j, k) in E else E_min')
    w( 4, 'vtk_points.InsertPoint( j + J * ( k + K*l), (x,y,z))')
    w( 1, 'vtk_grid.SetPoints( vtk_points)')

    ## data writer
    w( 1, 'vtk_writer = vtk.vtkXMLStructuredGridWriter()')
    w( 1, 'vtk_writer.SetDataModeToBinary()')
    w( 1, 'vtk_writer.SetCompressorTypeToZLib()')

    w( 1, 'T_data = _dataframe.groupby( _dataframe.index)')

    ## iterate over time and unroll columns
    w( 1, 'for t, ( T, D) in enumerate( T_data) :')
    for j, column in enumerate( columns) :
        w( 2, 'dataframe = D[["%s","%s"]]' % ( id_column, column))
        w( 2, 'cid_data,column_data = numpy.array( dataframe["%s"].values),numpy.array( dataframe["%s"].values)' % ( id_column, column))
        w( 2, 'vtkdata_%d = vtk.vtkFloatArray()' % ( j))
        w( 2, 'vtkdata_%d.SetName( "%%s" %% ( graphlabels["%s"]))' % ( j, column))
        w( 2, 'vtkdata_%d.SetNumberOfComponents( 1)' % ( j))
        w( 2, 'vtkdata_%d.SetNumberOfTuples( J*K*L)' % ( j))
        w( 2, 'for k in range( vtkdata_%d.GetNumberOfTuples()) :' % ( j))
        w( 3, 'vtkdata_%d.SetTuple1( k, %f)' % ( j, _graph.get_kindproperty( 'nodatavalue', -99.99)))
        w( 2, 'drop_cnt = 0')
        w( 2, 'for ( cid, value) in zip( cid_data, column_data) :')
        w( 3, 'l = 0')
        w( 3, 'if cid not in P :')
        w( 4, 'drop_cnt += 1')
        #w( 4, 'print( "dropping ID %d (%f)" % ( cid, value))')
        w( 4, 'continue')
        w( 3, 'for ( j, k) in P[cid] :')
        w( 4, 'vtkdata_%d.SetTuple1( j + J * ( k + K*l), value)' % ( j))
        w( 2, 'vtk_grid.GetPointData().AddArray( vtkdata_%d)' % ( j))
        w( 2, 'if drop_cnt > 0 :')
        w( 3, 'print( "dropped %%d elements for column \'%%s\'" %% ( drop_cnt, "%s"))' % column)

        w( 2, 'print( t,": ",T)')


    return  0

