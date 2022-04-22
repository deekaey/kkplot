
from kkutils.log import *
from kkengines.pythoncode import fitness
import matplotlib.dates as matplotlib_dates

def kkplot_pythonmatplotlib_time_shadebox( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_time_shadebox_%s( "%s", _dataframe=%s, _axes=%s)' % ( self._canonicalize_name( _id), _id, dataframe, axes)

    columns = _columns
    for auxialiary_columns in _auxialiary_columns :
        columns += auxialiary_columns

    ymin = _graph.get_property( 'ylimitlow', 0.0)
    ymax = _graph.get_property( 'ylimithigh', 1.0)

    w = self.W.iappendnl
    w( 0, 'def kkplot_plot_time_shadebox_%s( _id, _dataframe, _axes) :' % ( self._canonicalize_name( _id)))
    w( 1, '_axes.set_gid( _id)')

    w( 1, 'graphlabels = { %s }' % ( self._make_labels( columns, _graph, dataframe='_dataframe')))

    w( 1, 'columns = [ %s]' % ( ','.join([ '"%s"' % c for c in columns])))
    w( 1, 'for j, column in enumerate( columns) :')

    w( 2, 'this_shadebox = _axes.axvspan( *matplotlib_dates.datestr2num( [ "%s", "%s"]), ymin=%f, ymax=%f %s, label=graphlabels[column], gid="%%s" %% ( column))' \
        % ( str(_graph.domain.t_from), str(_graph.domain.t_to),
            ymin, ymax,
            self._make_args( 'l', \
                zorder=_graph.zorder, \
                facecolor=_graph.get_property( 'color'), \
                edgecolor=_graph.get_property( 'edgecolor'), \
                alpha=_graph.get_property( 'transparency'), \
                linestyle=self._get_linestyle( _graph.get_property( 'linestyle', 'solid')), \
                linewidth=_graph.get_property( 'linewidth') \
        )))
                #visible=self._toggle( _graph.get_property( 'hidden', False))

    if _graph.get_property( 'xlabel') :
        w( 2, 'XY = this_shadebox.get_xy()')
        w( 2, 'cx, cy = (XY[2][0]+XY[1][0])/2.0, XY[1][1]-0.01')
        w( 2, 'from matplotlib.transforms import blended_transform_factory')
        w( 2, 'c_transform = blended_transform_factory( _axes.transData, _axes.transAxes)')
        w( 2, '_axes.annotate( "%s", ( cx, cy), xycoords=c_transform, color="black", fontsize=%d, ha="center", va="top")' \
            % ( _graph.get_property( 'xlabel'), _graph.get_property( 'legendfontsize', 6)))

    return method_call

