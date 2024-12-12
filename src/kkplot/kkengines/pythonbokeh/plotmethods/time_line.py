
from kkplot.kkutils.log import *

def kkplot_pythonbokeh_time_line( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_time_line_%s( "%s", _dataframe=%s, _plot=%s)' % ( self._canonicalize_name( _id), _id, dataframe, axes)

    columns = _columns
    for auxialiary_columns in _auxialiary_columns :
        columns += auxialiary_columns

    c_lo, c_hi = ( 0.25, 1)

    w = self.W.iappendnl
    w( 0, 'import scipy')
    w( 0, 'scipy_version = scipy.__version__')
    w( 0, 'def kkplot_plot_time_line_%s( _id, _dataframe, _plot) :' % ( self._canonicalize_name( _id)))

    w( 1, 'graphlabels = { %s }' % ( self._make_labels( columns, _graph)))
    xcolumn = '_dataframe.index'


    w( 1, 'columns = [ %s]' % ( ','.join([ '"%s"' % c for c in columns])))
    w( 1, 'for j, column in enumerate( columns) :')
    ycolumn = '_dataframe[column]'

    color = ''
    if not _graph.get_property( "color"):
        if _graph.get_property( "colormap"):
            w( 2, 'col = %f + ( %f - %f) * float( j)/float( len( columns))' % ( c_lo, c_hi, c_lo))
            color = ', color=matplotlib.colors.to_hex( matplotlib_colormap.%s( col))' % ( _graph.get_property( "colormap"))
        else:
            w( 2, 'color_from_bokeh_colors = bokeh_colors[j % len(bokeh_colors)]')
            color = ', color=color_from_bokeh_colors'

    legend_label = ''
    if _graph.get_property( "legend_label", "True") in ["True", 'yes']:
        legend_label = ', legend_label=graphlabels[column].replace("$", "")'

    w( 2, '_plot.line( %s, %s %s %s %s)' \
        % ( xcolumn, ycolumn, color, legend_label, self._make_args( 'l', \
                              color=_graph.get_property( 'color'), \
                              line_width=_graph.get_property( 'linewidth', 1.0))))
    w( 2, 'if "%s" != "None" : ' %_graph.get_property( 'marker'))
    w( 3, 'if scipy_version >= "1.13.0":')
    w( 4, '_plot.scatter( %s, %s %s %s %s)' \
        % ( xcolumn, ycolumn, color, legend_label, self._make_args( 'l', \
                              color=_graph.get_property( 'color'), \
                              size=_graph.get_property( 'markersize', 1.0))))
    w( 3, 'else:')
    w( 4, '_plot.circle( %s, %s %s %s %s)' \
        % ( xcolumn, ycolumn, color, legend_label, self._make_args( 'l', \
                              color=_graph.get_property( 'color'), \
                              size=_graph.get_property( 'markersize', 1.0))))
    w( 2, '_plot.legend.label_text_font_size = "%spt"' %_graph.get_property( 'legend_fontsize', 10))
    w( 2, '_plot.legend.orientation = "%s"' %_graph.get_property( 'legend_orientation', "horizontal"))
    w( 2, '_plot.legend.border_line_alpha = %s' %_graph.get_property( 'legend_borderline_alpha', 0))
    w( 2, '_plot.legend.background_fill_alpha = %s' %_graph.get_property( 'legend_borderline_alpha', 0))
    w( 2, '_plot.legend.label_standoff = %s' %_graph.get_property( 'label_standoff', 5))
    w( 2, '_plot.legend.glyph_width = %s' %_graph.get_property( 'glyph_width', 10))
    w( 2, '_plot.legend.spacing = %s' %_graph.get_property( 'legend_spacing', 10))
    w( 2, '_plot.legend.padding = %s' %_graph.get_property( 'legend_padding', 3))
    w( 2, '_plot.legend.margin = %s' %_graph.get_property( 'legend_margin', 3))

#        #_plot.legend.border_line_alpha = 0.0        
#        #_plot.legend.background_fill_alpha = 0.0
#        _plot.legend.label_standoff = 5
#        _plot.legend.glyph_width = 5
#        _plot.legend.spacing = 10
#        _plot.legend.padding = 3
#        _plot.legend.margin = 3
    return method_call

