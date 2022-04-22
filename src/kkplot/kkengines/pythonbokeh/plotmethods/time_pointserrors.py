

from kkplot.kkutils.log import *

def kkplot_pythonbokeh_time_points_errors( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_time_pointserrors_%s( "%s", _dataframe=%s, _plot=%s)' % ( self._canonicalize_name( _id), _id, dataframe, axes)

    columns = _columns
    for auxialiary_columns in _auxialiary_columns :
        columns += auxialiary_columns

    c_lo, c_hi = ( 0.25, 1)

    w = self.W.iappendnl
    w( 0, 'def kkplot_plot_time_pointserrors_%s( _id, _dataframe, _plot) :' % ( self._canonicalize_name( _id)))

    xcolumn = '_dataframe.index'


    w( 1, 'columns = [ %s]' % ( ','.join([ '"%s"' % c for c in columns])))
    

    w( 1, 'if len( columns) != 2 :')
    w( 2, 'sys.stderr.write("error points plot needs exactly 2 arguments")')
    w( 2, 'sys.exit( 13)')
    
    ycolumn = '_dataframe[columns[0]]'
    
    color = ''
    if _graph.get_property( "colormap") and not _graph.get_property( "color"):
        w( 2, 'col = %f + ( %f - %f) * float( j)/float( len( columns))' % ( c_lo, c_hi, c_lo))
        color = ', color=matplotlib.colors.to_hex( matplotlib_colormap.%s( col))' % ( _graph.get_property( "colormap"))

    w( 1, 'if "%s" != "None" : ' %_graph.get_property( 'marker'))
    w( 2, '_plot.circle( %s, %s %s %s)' \
        % ( xcolumn, ycolumn, color, self._make_args( 'l', \
                              color=_graph.get_property( 'color'), \
                              size=_graph.get_property( 'markersize', 1.0))))

    w( 2, 'source_error = ColumnDataSource(data=dict(base=_dataframe.index, lower=_dataframe[columns[0]]-_dataframe[columns[1]]*0.5,  upper=_dataframe[columns[0]]+_dataframe[columns[1]]*0.5))')
    w( 2, '_plot.add_layout( Whisker(source=source_error, base="base", upper="upper", lower="lower"))')

    return method_call


