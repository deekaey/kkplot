
from kkplot.kkutils.log import *
from kkplot.kkutils import esri as shapefile
#from kkutils import rotate as rotate

#from vtk.util import numpy_support

def kkplot_pythonvtk_time_volume( self, _id, _graph, _columns, _auxialiary_columns, **_kwargs) :
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
        kklog_error( 'plot method requires kind property "extents" { (X,Y,Z), ESRI ShapeFile } [graph=%s]' % graphid)
        return None

    w( 0, 'def kkplot_plot_time_volume_%s( _id, _dataframe) :' % ( graphid))

    w( 1, 'graphlabels = { %s }' % ( self._make_labels( columns, _graph)))



    rc_grid = 0
    if isinstance( extents, list) and len( extents) in [ 2, 3 ] :
        w( 1, 'vtk_filename = "%s/%s.%%04d.vtr"' % ( outputdir, graphid))
        rc_grid = kkplot_pythonvtk_time_volume_rectilinear(
            self, _graph, columns, extents, dataframe, _kwargs)
    elif  isinstance( extents, str) and len( extents) > 0 :
        w( 1, 'vtk_filename = "%s/%s.%%04d.vtu"' % ( outputdir, graphid))
        rc_grid = kkplot_pythonvtk_time_volume_unstructured(
            self, _graph, columns, extents, dataframe, _kwargs)
    elif  isinstance( extents, dict) and len( extents) > 0 :
        w( 1, 'vtk_filename = "%s/%s.%%04d.vts"' % ( outputdir, graphid))
        rc_grid = kkplot_pythonvtk_time_volume_structured(
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


    method_call = 'kkplot_plot_time_volume_%s( "%s", _dataframe=%s)' \
         % ( graphid, _id, dataframe)
    return  method_call

def kkplot_pythonvtk_time_volume_unstructured( self, _graph, _columns, _extents, _dataframe, _kwargs) :
    w = self.writer.iappendnl

    meta_columns = list()
    id_column = None
    for column in _columns :
        if column.endswith( '.id') :
            id_column = column
            meta_columns.append( id_column)
    kklog_debug( 'id-column=%s' % id_column)
    z_column = None
    for column in _columns :
        if column.endswith( '.z') :
            z_column = column
            meta_columns.append( z_column)
    kklog_debug( 'z-column=%s' % z_column)
    Z_column = None
    for column in _columns :
        if column.endswith( '.Z') :
            Z_column = column
            meta_columns.append( Z_column)
    kklog_debug( 'Z-column=%s' % Z_column)
    if Z_column is None :
        kklog_error( 'plot method is missing "Z" column')
        return -1

    level_column = None
    for column in _columns :
        if column.endswith( '.level') :
            level_column = column
            meta_columns.append( level_column)
    kklog_debug( 'level-column=%s' % level_column)
    levels = [ 1 ]
    if level_column is None :
        if _graph.get_kindproperty( 'levels') :
            levels = _graph.get_kindproperty( 'levels')
        else :
            kklog_debug( 'plot method is missing "level" column, using 1 level with height 1')
    else :
        kklog_fatal( 'reading "level" information from output currently not supported :-(')

    n_levels = len( levels)
    zscale = _graph.get_kindproperty( 'zscale')

    value_columns = list()
    for column in _columns :
        if column not in meta_columns :
            value_columns.append( column)
    columns = value_columns

    ugrid = shapefile.Reader( '%s' % ( _extents))

    id_field = None
    id_field_name = _graph.get_kindproperty( 'idfield', 'ID')
    j = 0
    for f_j in ugrid.fields :
        if isinstance( f_j, tuple) :
            continue
        kklog_debug( 'field[%d]=\n%s [%s]' % ( j, f_j, ugrid.fields[j]))
        if f_j[0] == id_field_name :
            id_field = j
        j += 1
    if id_field is None :
        kklog_error( 'unable to find cell ID field; maybe provide mapping via kind property "idfield"')
        return -1

    lscale = 0.0
    levels0 = [0.0] + levels

    n_cells = len( ugrid.shapes())*len( levels)

    vtk_pointset_id_offsets = dict()
    vtk_point_id = 0
    vtk_pointset_id = 0
    w( 1, 'vtk_points = vtk.vtkPoints()')
    w( 1, 'vtk_grid = vtk.vtkUnstructuredGrid()')
    w( 1, 'vtk_grid.Allocate( %d, 1)' % ( n_cells))
    for j, s_j in enumerate( ugrid.iterShapeRecords()) :
        n_points = len( s_j.shape.points)

        cellid = s_j.record[id_field]
        vtk_pointset_id_offsets[cellid] = vtk_pointset_id
        for l, l_l in enumerate( levels0[:-1]) :
            w( 1, 'vtk_pointset_%d = vtk.vtkConvexPointSet()' % ( vtk_pointset_id))
            for k, p_k in enumerate( s_j.shape.points) :
                ## top plane
                w( 1, 'vtk_points.InsertPoint( %d, %f, %f, %f)' % ( vtk_point_id, p_k[0], p_k[1], -zscale*(l*lscale+levels0[l])))
                w( 1, 'vtk_pointset_%d.GetPointIds().InsertId( %d, %d)' % ( vtk_pointset_id, 2*k, vtk_point_id))
                vtk_point_id += 1
                ## bottom plane
                w( 1, 'vtk_points.InsertPoint( %d, %f, %f, %f)' % ( vtk_point_id, p_k[0], p_k[1], -zscale*(l*lscale+levels0[l+1])))
                w( 1, 'vtk_pointset_%d.GetPointIds().InsertId( %d, %d)' % ( vtk_pointset_id, 2*k+1, vtk_point_id))
                vtk_point_id += 1

            w( 1, 'vtk_grid.InsertNextCell( vtk_pointset_%d.GetCellType(), vtk_pointset_%d.GetPointIds())' % ( vtk_pointset_id, vtk_pointset_id))
            vtk_pointset_id += 1
    kklog_debug( '%s' % vtk_pointset_id_offsets)

    w( 1, 'vtk_grid.SetPoints( vtk_points)')

    ## data writer
    w( 1, 'vtk_writer = vtk.vtkXMLUnstructuredGridWriter()')
    w( 1, 'vtk_writer.SetDataModeToBinary()')
    w( 1, 'vtk_writer.SetCompressorTypeToZLib()')

#    LEVELLUT_SCALE = 1000000
#    w( 1, 'level_lut = { %s }' % ( ','.join( [ '%d:%d' % ( abs(int( LEVELLUT_SCALE*lvl)), l) for l, lvl in enumerate( levels)])))
    w( 1, 'id_to_pointsetoffset = %s' % ( str( vtk_pointset_id_offsets)))
#    w( 1, 'cell_to_pointset = lambda id, z : id_to_pointsetoffset[id]+level_lut[abs(int(%d*z))]' % ( LEVELLUT_SCALE))
    w( 1, 'cell_to_pointset = lambda id, l : id_to_pointsetoffset[id]+abs(l)')

    w( 1, 'T_data = _dataframe.groupby( _dataframe.index)')

#    w( 1, 'columns = [ %s]' % ( ','.join([ '"%s"' % c for c in columns])))

    w( 1, 'for t, ( T, D) in enumerate( T_data) :')
    for j, column in enumerate( columns) :
#    w( 2, 'for j, column in enumerate( columns) :')
        #w( 2, 'columnname = "%02d" % j')
        w( 2, 'dataframe = D[["%s","%s","%s"]]' % ( column, id_column, Z_column))
        w( 2, 'id_data,z_data,column_data = numpy.array( dataframe["%s"].values), numpy.array( dataframe["%s"].values), numpy.array( dataframe["%s"].values)' % ( id_column, Z_column, column))
        w( 2, 'vtkdata_%d = vtk.vtkFloatArray()' % ( j))
        w( 2, 'vtkdata_%d.SetName( "%%s" %% ( graphlabels["%s"]))' % ( j, column))
        w( 2, 'vtkdata_%d.SetNumberOfComponents( 1)' % ( j))
        w( 2, 'vtkdata_%d.SetNumberOfTuples( %d)' % ( j, n_cells))
        w( 2, 'print( len( id_data), len( z_data), len( column_data))')
        w( 2, 'for k, ( id, z, value) in enumerate( zip( id_data, z_data, column_data)) :')
#       w( 3, 'print k,"  z=",z, "id=",id, "  value=",value')
        w( 3, 'vtkdata_%d.SetTuple1( cell_to_pointset( id, z), value)' % ( j))
#       w( 3, 'vtk_grid.GetCellData().SetScalars( vtkdata_%d)' % ( j))
        w( 2, 'vtk_grid.GetCellData().AddArray( vtkdata_%d)' % ( j))


    return  0


def kkplot_pythonvtk_time_volume_rectilinear( self, _graph, _columns, _extents, _dataframe, _kwargs) :
    w = self.writer.iappendnl

    Nx, Ny, Nz = ( 0, 0, 1)
    if len( _extents) == 2 :
        Nx, Ny = _extents
    elif len( _extents) == 3 :
        Nx, Ny, Nz = _extents
    else :
        kklog_fatal( 'son of a gun..')

    meta_columns = list()
    x_column = None
    for column in _columns :
        if column.endswith( '.x') :
            x_column = column
            meta_columns.append( x_column)
    kklog_debug( 'x-column=%s' % x_column)
    y_column = None
    for column in _columns :
        if column.endswith( '.y') :
            y_column = column
            meta_columns.append( y_column)
    kklog_debug( 'y-column=%s' % y_column)
    z_column = None
    for column in _columns :
        if column.endswith( '.z') :
            z_column = column
            meta_columns.append( z_column)
    kklog_debug( 'z-column=%s' % z_column)
## sk:unused    level_column = None
## sk:unused    for column in _columns :
## sk:unused        if column.endswith( '.level') :
## sk:unused            level_column = column
## sk:unused            meta_columns.append( level_column)
## sk:unused    kklog_debug( 'level-column=%s' % level_column)
    levels = [ 0.0 ] * Nz
    if _graph.get_kindproperty( 'levels') :
        levels = _graph.get_kindproperty( 'levels')
        kklog_verbose( 'seeing "levels" property, adding these to given z values')
        if len( levels) != Nz :
            kklog_error( 'number of elements in "levels" property does not match Z-extent')
            return -1
    else :
        pass

    kklog_debug( 'columns=%s' % ( _columns))

    value_columns = list()
    for column in _columns :
        if column not in meta_columns :
            value_columns.append( column)
    columns = value_columns

    w( 1, 'Nx, Ny, Nz = ( %d, %d, %d)' % ( Nx, Ny, Nz))
    w( 1, 'dataframe_xyz = _dataframe[_dataframe.index==_dataframe.index[0]]')
##    w( 1, 'print( "len(D)=", len( dataframe_xyz))')

    zscale = _graph.get_kindproperty( 'zscale', 1.0)
    w( 1, 'levels = [ %s ]' % ( ','.join( [ '%f' % (zscale*v) for v in levels])))
    w( 1, 'dataframe_xyz = dataframe_xyz.sort_values( [ "%s", "%s", "%s" ] )' % ( x_column, y_column, z_column))
    w( 1, 'X = dataframe_xyz["%s"][0:Nx*Ny*Nz:Ny*Nz]' % ( x_column))
    w( 1, 'Y = dataframe_xyz["%s"][0:Ny*Nz:Nz]' % ( y_column))
    if _graph.get_kindproperty( 'levels') :
        w( 1, 'Z0 = min( dataframe_xyz["%s"][0:Nz])' % ( z_column))
        w( 1, 'Z = numpy.array( [ Z0 ] * Nz)')
    else :
        w( 1, 'Z = dataframe_xyz["%s"][0:Nz]' % ( z_column))
#    w( 1, 'print "X=",X, "Y=",Y, "Z=",Z')

    ## define grid coordinates
    w( 1, 'coords_X = vtk.vtkFloatArray()')
    w( 1, 'for coord_x in X :')
    w( 2, 'coords_X.InsertNextValue( coord_x)')
    w( 1, 'assert( len( X) == Nx)')
     
    w( 1, 'coords_Y = vtk.vtkFloatArray()')
    w( 1, 'for coord_y in Y :')
    w( 2, 'coords_Y.InsertNextValue( coord_y)')
    w( 1, 'assert( len( Y) == Ny)')
     
    w( 1, 'coords_Z = vtk.vtkFloatArray()')
    w( 1, 'level = 0.0')
    w( 1, 'for lvl, coord_z in zip( levels[::-1], Z) :')
    w( 2, 'level += lvl')
    w( 2, 'coords_Z.InsertNextValue( coord_z+level)')
    w( 1, 'assert( len( Z) == Nz)')

    ## define grid
    w( 1, 'vtk_grid = vtk.vtkRectilinearGrid()')
    w( 1, 'vtk_grid.SetDimensions( Nx, Ny, Nz)')
    w( 1, 'vtk_grid.SetXCoordinates( coords_X)')
    w( 1, 'vtk_grid.SetYCoordinates( coords_Y)')
    w( 1, 'vtk_grid.SetZCoordinates( coords_Z)')
    ## data writer
    w( 1, 'vtk_writer = vtk.vtkXMLRectilinearGridWriter()')
    w( 1, 'vtk_writer.SetDataModeToBinary()')
    w( 1, 'vtk_writer.SetCompressorTypeToZLib()')

    w( 1, 'T_data = _dataframe.groupby( _dataframe.index)')

    ## iterate over time and unroll columns
    w( 1, 'for t, ( T, D) in enumerate( T_data) :')
    for j, column in enumerate( columns) :
        w( 2, 'dataframe = D[["%s","%s","%s","%s"]].sort( [ "%s", "%s", "%s" ] )' \
            % ( column, z_column, y_column, x_column, z_column, y_column, x_column))
        w( 2, 'column_data = numpy.array( dataframe["%s"].values)' % ( column))
        w( 2, 'vtkdata_%d = vtk.vtkFloatArray()' % ( j))
        w( 2, 'vtkdata_%d.SetName( "%%s" %% ( graphlabels["%s"]))' % ( j, column))
        w( 2, 'vtkdata_%d.SetNumberOfComponents( 1)' % ( j))
        w( 2, 'vtkdata_%d.SetNumberOfTuples( Nx*Ny*Nz)' % ( j))
        w( 2, 'for k, value in enumerate( column_data) :')
##        w( 3, 'vtkdata_%d.InsertNextValue( value)' % ( j))
        w( 3, 'vtkdata_%d.SetTuple1( k, value)' % ( j))
##      w( 2, 'vtk_grid.GetCellData().AddArray( vtkdata_%d)' % ( j))
        w( 2, 'vtk_grid.GetPointData().AddArray( vtkdata_%d)' % ( j))

        w( 2, 'print( t,": ",T)')


    return  0

def kkplot_pythonvtk_time_volume_structured( self, _graph, _columns, _extents, _dataframe, _kwargs) :
    w = self.writer.iappendnl

    if len( _extents) != 2 :
        kklog_fatal( 'son of a gun..')

    indexmap = _extents.get( 'indexmap')
    if indexmap is None :
        return -1
    pointmap = _extents.get( 'pointmap')
    if pointmap is None :
        return -1

    if len( indexmap) != len( pointmap) :
        ## find common set
        im, pm = dict(), dict()
        for id in indexmap :
            if id in pointmap :
                im[id] = indexmap[id]
                pm[id] = pointmap[id]
        for id in pointmap :
            if id in indexmap :
                im[id] = indexmap[id]
                pm[id] = pointmap[id]
        indexmap = im
        pointmap = pm

    levels = [ 0.0 ] * 1
    if _graph.get_kindproperty( 'levels') :
        levels = _graph.get_kindproperty( 'levels')
        zscale = _graph.get_kindproperty( 'zscale', 1.0)
        level = 0.0
        Z = list()
        for lvl in levels :
            level += lvl * zscale
            Z.append( level)
        levels = Z
        kklog_verbose( 'seeing "levels" property, adding these to given z values')
    else :
        pass

## TODO  remove L
    J, K, L = set(), set(), set()
    for id, ( j,k,l) in zip( indexmap.keys(), indexmap.values()) :
        J.add( j)
        K.add( k)
        L.add( l)
    Nj, Nk, Nl = ( 1+max( J)-min( J), 1+max( K)-min( K), len( levels)) #1+max( L)-min( L))
    ## shift to (0,0,0)
    I = dict()
    for id, ( j,k,l) in zip( indexmap.keys(), indexmap.values()) :
        I[id] = ( j-min(J), k-min(K), l-min(L))
    indexmap = I

    del J
    del K
    del L

    meta_columns = list()
    id_column = None
    for column in _columns :
        if column.endswith( '.id') :
            id_column = column
            meta_columns.append( id_column)
    kklog_debug( 'id-column=%s' % id_column)
    z_column = None
    for column in _columns :
        if column.endswith( '.z') :
            z_column = column
            meta_columns.append( z_column)
    kklog_debug( 'z-column=%s' % z_column)

    kklog_debug( 'columns=%s' % ( _columns))

    value_columns = list()
    for column in _columns :
        if column not in meta_columns :
            value_columns.append( column)
    columns = value_columns

    
    Q = dict()
    for id, ( j,k,l) in zip( indexmap.keys(), indexmap.values()) :
        Q[( j,k)] = id
    w( 1, 'I = %s' % ( indexmap))
    w( 1, 'Q = %s' % ( Q))
    w( 1, 'P = %s' % ( pointmap))
    w( 1, 'levels = %s' % ( levels))

    ## define grid
    w( 1, 'Nj, Nk, Nl = ( %d, %d, %d)' % ( Nj, Nk, Nl))
    w( 1, 'vtk_grid = vtk.vtkStructuredGrid()')
    w( 1, 'vtk_grid.SetDimensions( Nj, Nk, Nl)')
    w( 1, 'vtk_points = vtk.vtkPoints()')
    w( 1, 'vtk_points.SetNumberOfPoints( Nj*Nk*Nl)')
    w( 1, 'for j in xrange( Nj) :')
    w( 2, 'for k in xrange( Nk) :')
    w( 3, 'if ( j, k) in Q :')
    w( 4, 'x,y,z = P[Q[(j,k)]]')
    w( 4, 'for l in xrange( Nl) :')
    w( 5, 'z += levels[l]')
    w( 5, 'vtk_points.InsertPoint( j + Nj * ( k + Nk*l), (x,y,z))')
    w( 1, 'vtk_grid.SetPoints( vtk_points)')

    w( 1, 'id_to_index = lambda cid, l : I[cid][0] + Nj * ( I[cid][1] + Nk*abs(l))')

    ## data writer
    w( 1, 'vtk_writer = vtk.vtkXMLStructuredGridWriter()')
    w( 1, 'vtk_writer.SetDataModeToBinary()')
    w( 1, 'vtk_writer.SetCompressorTypeToZLib()')

    w( 1, 'T_data = _dataframe.groupby( _dataframe.index)')

    ## iterate over time and unroll columns
    w( 1, 'for t, ( T, D) in enumerate( T_data) :')
    for j, column in enumerate( columns) :
        w( 2, 'dataframe = D[["%s","%s","%s"]]' % ( id_column, z_column, column))
        w( 2, 'cid_data,z_data,column_data = numpy.array( dataframe["%s"].values),numpy.array( dataframe["%s"].values),numpy.array( dataframe["%s"].values)' % ( id_column, z_column, column))
        w( 2, 'vtkdata_%d = vtk.vtkFloatArray()' % ( j))
        w( 2, 'vtkdata_%d.SetName( "%%s" %% ( graphlabels["%s"]))' % ( j, column))
        w( 2, 'vtkdata_%d.SetNumberOfComponents( 1)' % ( j))
        w( 2, 'vtkdata_%d.SetNumberOfTuples( Nj*Nk*Nl)' % ( j))
        w( 2, 'for k in xrange( vtkdata_%d.GetNumberOfTuples()) :' % ( j))
        w( 3, 'vtkdata_%d.SetTuple1( k, %f)' % ( j, _graph.get_kindproperty( 'nodatavalue', -99.99)))
        w( 2, 'for k, ( cid, z, value) in enumerate( zip( cid_data, z_data, column_data)) :')
##        w( 3, 'vtkdata_%d.InsertNextValue( value)' % ( j))
        w( 3, 'vtkdata_%d.SetTuple1( id_to_index( cid, z), value)' % ( j))
##      w( 2, 'vtk_grid.GetCellData().AddArray( vtkdata_%d)' % ( j))
        w( 2, 'vtk_grid.GetPointData().AddArray( vtkdata_%d)' % ( j))

        w( 2, 'print( t,": ",T)')


    return  0

