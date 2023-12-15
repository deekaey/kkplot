
from kkplot.kkengines.pythonmatplotlib.plotmethods import kkplot_pythonmatplotlib_time_line
def kkplot_pythonmatplotlib_time_annotate( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    method_call = 'kkplot_plot_time_annotate_%s( "%s", _axes=%s, _graphresults=%s)' \
        % ( self._canonicalize_name( _id), _id, axes, _kwargs['graphresults'])

    columns = _columns
    for aux_columns in _auxialiary_columns :
        columns += aux_columns

    w = self.W.iappendnl
    w( 0, 'from scipy import stats')
    w( 0, 'def kkplot_plot_time_annotate_%s( _id, _axes, _graphresults) :' \
        % ( self._canonicalize_name( _id)))
    w( 1, '_axes.set_gid( _id)')

    w( 1, 'graphid = "%s"' % ( _graph.graphid))
    w( 1, 'eval_stats_names = [ %s]' \
        % ( ','.join( [ ','.join( '"%s"' % ( dep) for dep in _graph.dependencies( column)) for column in columns if not _graph.is_graphresult( column)])))

    w( 1, '%s_x = pandas.DataFrame({"datetime": _graphresults[eval_stats_names[0]][0], eval_stats_names[0]: _graphresults[eval_stats_names[0]][1]})' % ( _graph.graphid.replace('.', '_')))
    w( 1, '%s_y = pandas.DataFrame({"datetime": _graphresults[eval_stats_names[1]][0], eval_stats_names[1]: _graphresults[eval_stats_names[1]][1]})' % ( _graph.graphid.replace('.', '_')))
    w( 1, 'res = pandas.concat([%s_x.set_index("datetime"), %s_y.set_index("datetime")], axis=1, join="inner")' % ( _graph.graphid.replace('.', '_'), _graph.graphid.replace('.', '_')))
    w( 1, 'rmse = ((res[eval_stats_names[1]] - res[eval_stats_names[0]]) ** 2).mean() ** 0.5')
    w( 1, 'slope, intercept, r_value, p_value, std_err = stats.linregress(res[eval_stats_names[0]], res[eval_stats_names[1]])')
    w( 1, 'r2 = r_value ** 2.0')
    coords = _graph.get_property( 'textcoordinates', [0.05, 0.92])
    w( 1, 'textcoordinates=[%f, %f]' %(coords[0], coords[1]))
    w( 1, 'text = "%s"' %("%s" %_graph.get_property( 'text', '')))
    w( 1, '_axes.annotate( %s (text, %s), xy=(0.0,0.0), xycoords="axes fraction", xytext=(textcoordinates[0], textcoordinates[1]), textcoords="axes fraction")' % ("'%s: %f' %", _graph.get_property( 'stats', 'rmse')))
    return method_call