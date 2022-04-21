
from kkengines.pythonbokeh.plotmethods import kkplot_pythonbokeh_time_line
def kkplot_pythonbokeh_time_points( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    _graph.add_properties( { 'linewidth': 1.0e-9} )
    if _graph.get_property( 'marker') is None :
        _graph.add_properties( { 'marker': '.'})

    return kkplot_pythonbokeh_time_line( self, \
        _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs)

