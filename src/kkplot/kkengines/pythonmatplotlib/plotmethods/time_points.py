
from kkengines.pythonmatplotlib.plotmethods import kkplot_pythonmatplotlib_time_line
def kkplot_pythonmatplotlib_time_points( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    _graph.add_properties( { 'linewidth': 0.0} )
    if _graph.get_property( 'marker') is None :
        _graph.add_properties( { 'marker': '.'})

    return kkplot_pythonmatplotlib_time_line( self, \
        _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs)

