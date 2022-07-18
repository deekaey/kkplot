
## example call
## python kkplot.py -E matplotlib examples/config.yml
##
## supported output formats:
##  eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff

from kkplot.kkengines.base import kkplot_engine as kkplot_engine
from kkplot.kkengines.base import kkplot_plotmethod as kkplot_plotmethod
from kkplot.kkplot_dviplot import kkplot_dviplot as kkplot_dviplot

from kkplot.kkutils.log import *
from kkplot.kkutils import writer as kkplot_writer

from kkplot.kkengines.pythonmatplotlib.plotmethods import *

import sys
import time

KKPLOT_MATPLOTLIB_UNSET_AXES_GID = '''
    ## unset axes' GID
    for ax in kkaxes.values() :
        ax.set_gid( None)

'''
KKPLOT_MATPLOTLIB_DELETE_AXES_WITHOUT_GRAPHS = '''
    ## delete empty axes
    for ax in kkaxes.values() :
        if ax.get_gid() is None :
            kkfigures.delaxes( ax)

'''

KKPLOT_MATPLOTLIB_RUN_USER_CODE = '''
    ## run user code
    if user_code_available :
        user_code.customize_figure( kkfigures)

'''

KKPLOT_MATPLOTLIB_TIMEDELTA = '''
class kkplot_matplotlib_timedelta( object) :
    def __init__( self, _timedelta) :
        self._td = _timedelta
        
    @property
    def seconds( self) :
        return float( self._td.days * 86400 + self._td.seconds)
    @property
    def minutes( self) :
        return float( self._td.days * 1440 + self._td.seconds//60)
    @property
    def hours( self) :
        return float( self._td.days * 24 + self._td.seconds//3600)
    @property
    def days( self) :
        return float( self._td.days)
'''

KKPLOT_MATPLOTLIB_TIMEPERIOD = '''
class kkplot_matplotlib_timeperiod( object) :
    def __init__( self, _timedelta) :
        self._td = kkplot_matplotlib_timedelta( _timedelta)

    @property
    def seconds( self) :
        return self._td.seconds + 1.0
    @property
    def minutes( self) :
        return self._td.minutes + 1.0
    @property
    def hours( self) :
        return self._td.hours + 1.0
    @property
    def days( self) :
        return self._td.days + 1.0
'''

## https://github.com/matplotlib/matplotlib/issues/537
KKPLOT_MATPLOTLIB_ORTHOGONALPROJECTION = '''
def kkplot_orthogonal_proj( zfront, zback) :
    a = ( zfront + zback) / ( zfront - zback)
    b = -2 * ( zfront * zback) / ( zfront - zback)
    return numpy.array([[ 1, 0, 0,       0],
                        [ 0, 1, 0,       0],
                        [ 0, 0, a,       b],
                        [ 0, 0, -0.0001, zback]])
try :
    from mpl_toolkits.mplot3d import proj3d
    proj3d.persp_transformation = kkplot_orthogonal_proj
except ImportError :
    sys.stderr.write( "failed to import 'proj3d' .. you should be OK...")
'''

KKPLOT_MATPLOTLIB_SORTBYZORDER = '''
def kkplot_sort_by_zorder( _handles, _labels) :
    z_h = list()
    for handle in _handles :
        if hasattr( handle, 'get_zorder') :
            z_h.append( handle.get_zorder())
        else :
            z_h.append( 0)

    z_H = [ 0] * len( _handles)
    for k1, z1 in enumerate( z_h) :
       for k2, z2 in enumerate( z_h) :
           if k1 == k2 :
               continue
           if z1 > z2 or ( z1==z2 and k2>k1) :
               z_H[k2] += 1

    new_handles = [ None] * len( _handles)
    new_labels = [ ''] * len( _handles)
    for k, (handle, label) in enumerate( zip( _handles, _labels)) :
        new_handles[z_H[k]], new_labels[z_H[k]] = handle, label
    return ( new_handles, new_labels)
'''

class Code( object) :
    def __init__( self, _code) :
        self.m_code = _code
    def  __str__( self) :
        return self.m_code

class kkplot_engine_matplotlib( kkplot_engine) :
    def  __init__( self, _conf=None, _dviplot=None) :
        super( kkplot_engine_matplotlib, self).__init__( "matplotlib", _conf, _dviplot)

        self.W = None

        kkplot_plotmethods = dict( \
            time_area=kkplot_pythonmatplotlib_time_area, \
            time_fill=kkplot_pythonmatplotlib_time_fill, \
            time_heatmap=kkplot_pythonmatplotlib_time_heatmap, \
            time_histogram=kkplot_pythonmatplotlib_time_histogram, \
            time_integratebar=kkplot_pythonmatplotlib_time_integratebar, \
            time_line=kkplot_pythonmatplotlib_time_line, \
            time_cumulativeline=kkplot_pythonmatplotlib_time_cumulativeline, \
            time_pie=kkplot_pythonmatplotlib_time_pie, \
            time_bars=kkplot_pythonmatplotlib_time_bars, \
            time_boxes=kkplot_pythonmatplotlib_time_boxes, \
            time_points=kkplot_pythonmatplotlib_time_points, \
            time_points_errors=kkplot_pythonmatplotlib_time_points_errors, \
            time_raster=kkplot_pythonmatplotlib_time_raster, \
            time_regressionline=kkplot_pythonmatplotlib_time_regressionline, \
            time_regressionpoint=kkplot_pythonmatplotlib_time_regressionpoint, \
            time_regressionzero=kkplot_pythonmatplotlib_time_regressionzero, \
            time_scatter=kkplot_pythonmatplotlib_time_scatter, \
            time_shadebox=kkplot_pythonmatplotlib_time_shadebox, \
            time_surface3d=kkplot_pythonmatplotlib_time_surface3d, \
            space_polygons=kkplot_pythonmatplotlib_space_polygons, \
            space_boxes=kkplot_pythonmatplotlib_space_boxes, \
            space_line3d=kkplot_pythonmatplotlib_space_line3d, \
            space_points3d=kkplot_pythonmatplotlib_space_points3d, \
            space_surface3d=kkplot_pythonmatplotlib_space_surface3d, \
            non_bartable=kkplot_pythonmatplotlib_non_bartable, \
            non_integratebar=kkplot_pythonmatplotlib_time_integratebar, \
            non_line=kkplot_pythonmatplotlib_non_line, \
            none=None)
        self.add_plotmethods( kkplot_plotmethods)

    @property
    def writer( self) :
        return self.W

    def  new( self, _conf, _dviplot) :
        enginematplotlib = kkplot_engine_matplotlib( _conf, _dviplot)
        enginematplotlib.W = kkplot_writer( _stream=None, _mode='python')
        return  enginematplotlib

    def  __str__( self) :
        return  self.name;

    def  help( self) :
        help_text = 'available graph types: { %s }' \
            % ( ', '.join( [ '\'%s\'' % ( plotmethod) for plotmethod in self.plotmethods]))
        return help_text

    def  generate( self) :

        self.generate_preamble( self._dviplot)
        self.generate_plots()
        self.generate_postamble()

        return 0

    def  write( self, _target=None) :
        self.W.write( _target=_target)
    @property
    def suffix( self) :
        return 'py'

    def generate_plots( self) :

        graphmethods = self.generate_plots_graphmethods()
        if len( graphmethods) == 0 :
            return

        self.generate_plots_auxiliarycode()
        self.generate_plots_createfigure()

        self.W.iappendnl( 0, '')

        self.generate_plots_graphmethodcalls( graphmethods)
        self.generate_plots_deleteemptyaxes()
        self.generate_plots_setplotproperties()
        self.generate_plots_setgraphproperties()

        self.W.append( KKPLOT_MATPLOTLIB_RUN_USER_CODE)

        self.generate_plots_writefigure()

        self.W.newline()
        self.W.iappendnl( 1, 'return kkfigures, kkaxes')

    def generate_plots_auxiliarycode( self) :
        pass

    def generate_plots_createfigure( self) :
        self.W.appendnl( '\n\ndef create_figure() :')
        self.generate_layout()

    def generate_layout( self) :
        self.W.iappendnl( 1, '')
        self.W.iappendnl( 1, 'kkfigures = matplotlib_pyplot.figure()')
        self.W.iappendnl( 1, 'kkaxes = dict()')
        for plot in self.dviplot.plots :
            ax_index = self._axis_index( plot)
            ax_position = self._axis_position( plot)
            projection = ''
            if plot.get_property( 'projection') :
                projection = ', projection="%s"' % ( plot.get_property( 'projection'))
            ## NOTE  sharex, sharey
            self.W.iappendnl( 1, 'kkaxes["%s"] = \\' % ( ax_index))
            self.W.iappendnl( 2, 'matplotlib_pyplot.subplot2grid((%d, %d), (%s), colspan=%d, rowspan=%d%s %s)' \
                % ( self.dviplot.extent_y, self.dviplot.extent_x, ax_position, \
                    plot.span_x, plot.span_y, projection, self._make_args( 'l', facecolor=plot.get_property( 'backgroundcolor'))))
            twinx = plot.get_property( 'twinx', True)
            if (plot.get_property( 'projection', '') != '3d') and twinx :
                self.W.iappendnl( 1, 'kkaxes["%s.twin"] = kkaxes["%s"].twinx()' % ( ax_index, ax_index))

            ticklabelformat = plot.get_property( 'ticklabelformat', False)
            self.W.iappendnl( 1, 'kkaxes["%s"].ticklabel_format(useOffset=%s)' % ( ax_index, ticklabelformat))


            axiscolor = plot.get_property( 'axiscolor', None)
            axiscolorbottom = plot.get_property( 'axiscolorbottom', axiscolor)
            if axiscolorbottom is None :
                self.W.comment_on()
                axiscolorbottom = "<color>"
            self.W.iappendnl( 1, 'kkaxes["%s"].spines["bottom"].set_color( "%s")' % ( ax_index, axiscolorbottom))
            self.W.comment_off()
            axiscolortop = plot.get_property( 'axiscolortop', axiscolor)
            if axiscolortop is None :
                self.W.comment_on()
                axiscolortop = "<color>"
            self.W.iappendnl( 1, 'kkaxes["%s"].spines["top"].set_color( "%s")' % ( ax_index, axiscolortop))
            self.W.comment_off()
            axiscolorright = plot.get_property( 'axiscolorright', axiscolor)
            if axiscolorright is None :
                self.W.comment_on()
                axiscolorright = "<color>"
            self.W.iappendnl( 1, 'kkaxes["%s"].spines["right"].set_color( "%s")' % ( ax_index, axiscolorright))
            self.W.comment_off()
            axiscolorleft = plot.get_property( 'axiscolorleft', axiscolor)
            if axiscolorleft is None :
                self.W.comment_on()
                axiscolorleft = "<color>"
            self.W.iappendnl( 1, 'kkaxes["%s"].spines["left"].set_color( "%s")' % ( ax_index, axiscolorleft))
            self.W.comment_off()

            axislinewidth = plot.get_property( 'axislinewidth', None)
            if axislinewidth is None :
                axislinewidth = 1.0
                self.W.comment_on()
            for side in [ "bottom", "left", "top", "right"] :
                self.W.iappendnl( 1, 'kkaxes["%s"].spines["%s"].set_linewidth( %.4f)' % ( ax_index, side, axislinewidth))
            self.W.comment_off()

        self.W.iappendnl( 1, 'kkfigures.set_size_inches( %f, %f)' \
            % ( self.dviplot.size_x, self.dviplot.size_y))

    def generate_plots_graphmethods( self) :
        self.W.iappendnl( 0, '')

        graph_method_calls = list()

        ## add plots
        for graph, plot in self.dviplot :
            ax_index = self._axis_index( plot)

            if graph.domain is None :
                continue

            graph_columns = list()
            auxialiary_columns = list()
            for dataselect in graph :
                aux_column_ids = graph.referenceids( dataselect)
                column_id = []
                if len( aux_column_ids) > 0 :
                    column_id = aux_column_ids.pop( 0) ## discard column_id

                graph_columns.append( column_id)
                auxialiary_columns.append( aux_column_ids)
                #kklog_debug( 'columns = %s' % ( ';'.join( [column_id]+aux_column_ids)))

                column_ids = graph.referenceids( dataselect)
                column_names = graph.names
                add_datalabel = graph.get_property( 'datalabel', True)
                for ( column_id, column_name) in zip( column_ids, column_names) :
                    graph_label = graph.label( column_name)
                    if graph_label is None :
                        column_label = None
                    elif add_datalabel :
                        column_label = '%s%s' % ( graph_label, graph.datalabel( dataselect, ' [%s]'))
                    else :
                        column_label = '%s' % ( graph_label)
                    graph.add_properties( { 'label.%s' % ( column_id): column_label})

            plotmethod = self.get_plotmethod( graph)
            if plotmethod :
                if graph.get_property( 'yaxisat', 'left') == 'left' :
                    pass
                elif graph.get_property( 'yaxisat', 'left') == 'right' :
                    ax_index += '.twin'
                else :
                    kklog_warn( 'graph property \'yaxisat\' has invalid value (%s); must be { %s, %s}' \
                        % ( graph.get_property( 'yaxisat'), 'left', 'right'))

                graph_method_call = plotmethod( self, graph.graphid, graph, ax_index, graph_columns, auxialiary_columns, \
                    graphresults='graphresults', axes='kkaxes', \
                    dataframe='kkdataframes["%s"]' % ( graph.graphid), figure='kkfigures')
                if graph_method_call is None :
                    kklog_error( 'failed to generate code for graph "%s"' % ( graph.graphid))
                    return list()
                graph_method_calls.append( kkplot_plotmethod( graph, graph_method_call))
            else :
                pass

        return  graph_method_calls

    def as_attr( self, _id, _obj, _propertyname, _propertydefaultvalue) :
        propertyvalue = getattr( _obj, _propertyname, _propertydefaultvalue)
        return ( _id, _propertyname, self._stringify( propertyvalue))

    def generate_plots_graphmethodcalls( self, _graphmethods) :
        w = self.W.iappendnl

        w( 0, '')
        w( 1, 'graphresults = dict()')
        w( 1, 'kkdataframes = dict()')

        seriesopts = dict( time=', parse_dates=["time"], index_col=1, keep_date_col=True', space='', non='')
        delim = self._conf.tmpdata_column_delim
        ## add graphs
        for graphmethod in _graphmethods :
            graphid = graphmethod.graph.graphid
            if self.dviplot.series_exists( graphid) :
                w( 1, 'try :')
                w( 2, 'kkdataframes["%s"] = pandas.read_csv( "%s", ' % ( graphid, self.dviplot.datapool_filename( graphid)) +
                    'header=0, na_values=["na"], sep="%s"' % ( delim) + seriesopts[graphmethod.graph.domainkind] + ')')
                w( 1, 'except :')
                w( 2, r'sys.stderr.write( "failed to open datafile  [datafile=%s]\n")' % ( self.dviplot.datapool_filename( graphid)))
                w( 2, r'sys.exit( 13)')

            w( 1, 'graphresults["%s"] = \\' % ( graphmethod.graph.graphresult))
            w( 2, graphmethod.methodcall)

    def generate_plots_deleteemptyaxes( self) :
        self.W.append( KKPLOT_MATPLOTLIB_DELETE_AXES_WITHOUT_GRAPHS)
    def generate_plots_setgraphproperties( self) :
        w = self.W.iappendnl
        ## rerender legends
        for plot in self.dviplot.plots :
            self.W.newline()
            ax_index = self._axis_index( plot)
            w( 1, '## legend properties for plot "%s"' % ( ax_index))
            w( 1, 'axes = kkaxes["%s"]' % ( ax_index))
            w( 1, 'handles, labels = axes.get_legend_handles_labels()')
            w( 1, 'if len( handles) == 0 :')
            w( 2, 'axes.legend_ = None')
            w( 1, 'else :')
            w( 2, 'handles, labels = kkplot_sort_by_zorder( handles, labels)')
            w( 2, 'axes_legend = axes.legend( handles, labels %s, frameon=False, fancybox=True, shadow=None)' \
                % self._make_args( 'l',
                    loc=plot.get_property( 'legendlocation', 'best'),
                    ncol=plot.get_property( 'legendcolumns', 1),
                    columnspacing=plot.get_property( 'legendcolumnspacing'),
                    fontsize=plot.get_property( 'legendfontsize'),
                    title=plot.get_property( 'legendtitle')
            ))
            if plot.get_property( 'legendtitlefontsize') :
                w( 2, 'if axes_legend.get_title() :')
                w( 3, 'axes_legend.get_title().set_fontsize(%s)' % ( float( plot.get_property( 'legendtitlefontsize'))))
            w( 2, 'axes_legend.set_zorder( 10000)')


    def generate_plots_setplotproperties( self) :
        w = self.W.iappendnl
        for plot in self.dviplot.plots :
            axis = self._axis_index( plot)
            w( 1, '')
            w( 1, '(x0, x1), (y0, y1) = kkaxes["%s"].get_xlim(), kkaxes["%s"].get_ylim()' % ( axis, axis))
            self.generate_plots_setplotproperty( plot)

    def generate_plots_setplotproperty( self, _plot) :
        self._setplotproperty( _plot, 'bgcolor', 'set_axis_bgcolor')
        self._setplotproperty( _plot, 'xlabel', 'set_xlabel')
        self._setplotproperty( _plot, 'xlabelfontsize', 'xaxis.label.set_size')
        self._setplotproperty( _plot, 'ylabel', 'set_ylabel')
        self._setplotproperty( _plot, 'ylabelfontsize', 'yaxis.label.set_size')
        self._setplotpropertytwin( _plot, 'ylabelright', 'set_ylabel')
        self._setplotpropertytwin( _plot, 'ylabelrightfontsize', 'yaxis.label.set_size')
        self._setplotproperty( _plot, 'zlabel', 'set_zlabel')

        if _plot.get_property( 'square', False) == True :
            value = Code( 'abs( x1-x0) / abs( y1-y0)')
            self._setplotproperty( _plot, 'square', 'set_aspect', value)

        if _plot.get_property( 'xticks', False) is None or _plot.get_property( 'xticks') is False :
            _plot.add_properties( dict( xticks=[]))
        elif isinstance( _plot.get_property( 'xticks'), list) :
            _plot.add_properties( dict( xticks=_plot.get_property( 'xticks')))
        else :
            _plot.add_properties( dict( xticks=None))
        self._setplotproperty( _plot, 'xticks', 'set_xticks')

        if _plot.get_property( 'yticks', False) is None or _plot.get_property( 'yticks') is False :
            _plot.add_properties( dict( yticks=[]))
        elif isinstance( _plot.get_property( 'yticks'), list) :
            _plot.add_properties( dict( yticks=_plot.get_property( 'yticks')))
        else :
            _plot.add_properties( dict( yticks=None))
        self._setplotproperty( _plot, 'yticks', 'set_yticks')


        if _plot.get_property( 'xticklabels', False) is None or _plot.get_property( 'xticklabels') is False :
            _plot.add_properties( dict( xticklabels=[]))
        elif isinstance( _plot.get_property( 'xticklabels'), list) :
            _plot.add_properties( dict( xticklabels=[ "%s" % ( str( lbl)) for lbl in _plot.get_property( 'xticklabels')]))
        else :
            _plot.add_properties( dict( xticklabels=None))
        self._setplotproperty( _plot, 'xticklabels', 'set_xticklabels')

        if _plot.get_property( 'yticklabels', False) is None or _plot.get_property( 'yticklabels') is False :
            _plot.add_properties( dict( yticklabels=[]))
        elif isinstance( _plot.get_property( 'yticklabels'), list) :
            _plot.add_properties( dict( yticklabels=[ "%s" % ( str( lbl)) for lbl in _plot.get_property( 'yticklabels')]))
        else :
            _plot.add_properties( dict( yticklabels=None))
        self._setplotproperty( _plot, 'yticklabels', 'set_yticklabels')

        self._setplotxyticklabelsrotation( _plot)

        self._setplotproperty( _plot, 'grid', 'grid')
        self._setplotproperty( _plot, 'align', 'axis', _value='tight', _bool=False)
        _plot.add_properties( dict( title=''))
        if _plot.title is not None :
            _plot.add_properties( dict( title=_plot.title))
        self._setplotproperty( _plot, 'title', 'set_title')

        if ( _plot.get_property( 'xlimitlow', False) not in ['None', '']) and ( _plot.get_property( 'xlimithigh', False) not in ['None', '']) :
            self._setplotproperty( _plot, 'xlimitlow,xlimithigh', 'set_xlim')
        self._setplotproperty( _plot, 'ylimitlow,ylimithigh', 'set_ylim')
        self._setplotproperty( _plot, 'zlimitlow,zlimithigh', 'set_zlim')

    def _setplotproperty( self, _plot, _props, _setter, _value=None, _bool=None) :
        axis = self._axis_index( _plot)
        self.__setplotproperty( _plot, axis, _props, _setter, _value, _bool)
    def _setplotpropertytwin( self, _plot, _props, _setter, _value=None, _bool=None) :
        axis = self._axis_index( _plot)
        self.__setplotproperty( _plot, '%s.twin' % ( axis), _props, _setter, _value, _bool)

    def __setplotproperty( self, _plot, _axis, _props, _setter, _value=None, _bool=None) :
        self.W.comment_off()
        values = list()
        for prop in _props.split( ',') :
            if _plot.get_property( prop) is not None :
                if _bool is not None and _plot.get_property( prop) != _bool :
                    self.W.comment_on()
                values.append( _value if _value is not None else _plot.get_property( prop))
            else :
                values = ['<%s>' % ( _props)]
                self.W.comment_on()
                break
        property_code = 'kkaxes["%s"].%s( %s)' \
            % ( _axis, _setter, ', '.join( [ self._stringify( value) for value in values]))

        self.W.iappendnl( 1, '%s' % ( property_code))
        self.W.comment_off()

    def _setplotxyticklabelsrotation( self, _plot) :
        ax_index = self._axis_index( _plot)
        if _plot.get_property( 'xticklabelsrotation') is None :
            self.W.comment_on()
        self.W.iappendnl( 1, 'for ticklabel in kkaxes["%s"].%s() :' % ( ax_index, 'get_xticklabels'))
        self.W.iappendnl( 2, 'ticklabel.set_rotation( %s)' % ( str( _plot.get_property( 'xticklabelsrotation', '"<float>"'))))
        self.W.comment_off()

        if _plot.get_property( 'yticklabelsrotation') is None :
            self.W.comment_on()
        self.W.iappendnl( 1, 'for ticklabel in kkaxes["%s"].%s() :' % ( ax_index, 'get_yticklabels'))
        self.W.iappendnl( 2, 'ticklabel.set_rotation( %s)' % ( str( _plot.get_property( 'yticklabelsrotation', '"<float>"'))))
        self.W.comment_off()

    def generate_plots_writefigure( self) :
        self.W.iappendnl( 0, '')

        tl_left, tl_bottom, tl_right, tl_top = ( 0.0, 0.0, 1.0, 1.0)
        if self.dviplot.title :
            self.W.iappendnl( 1, 'kkfigures.suptitle( "%s", fontsize=%d)' % ( self.dviplot.title, 20))
            tl_top = 0.95
        self.W.iappendnl( 1, 'sys.stderr.write( \'writing "%s"...\\n\')' % ( self.dviplot.outputfile))
        if self.dviplot.get_property( 'tight', True) == True :
            self.W.iappendnl( 1, 'kkfigures.set_tight_layout( dict( rect=[%.2f, %.2f, %.2f, %.2f])) #pad=1.08, h_pad=2.0, w_pad=2.0))' % ( tl_left, tl_bottom, tl_right, tl_top))
        if self.dviplot.get_property( 'padtop') is not None :
            self.W.iappendnl( 1, 'kkfigures.subplots_adjust( top=0.85)')
        self.W.iappendnl( 1, 'kkfigures.savefig( "%s", format="%s", dpi=%f, transparent=%s, pad_inches=%f, facecolor="%s")' \
            % ( self.dviplot.outputfile, self.dviplot.outputfileformat, 100, False, 0.1, "white"))
        self.W.iappendnl( 1, 'matplotlib_pyplot.close( kkfigures)')

    def generate_preamble( self, _dviplot) :
        self.W.appendnl( '# vim: ft=python')
        self.W.appendnl( '## generated by kkplot on %s\n' % ( time.strftime( '%Y, %b. %d %H:%M')))
        self.W.appendnl( 'import sys as sys')
        self.W.appendnl( 'import math as math')
        self.W.appendnl( 'import datetime as datetime')
        self.W.appendnl( 'import pandas as pandas')
        self.W.appendnl( 'import numpy as numpy')
        self.W.appendnl( 'import matplotlib as matplotlib')
        self.W.appendnl( 'matplotlib.use( "Agg")')
        self.W.appendnl( 'import matplotlib.cm as matplotlib_colormap')
        self.W.appendnl( 'import matplotlib.dates as matplotlib_dates')
        self.W.appendnl( 'import matplotlib.lines as matplotlib_lines')
        self.W.appendnl( 'import matplotlib.pyplot as matplotlib_pyplot')
        self.W.appendnl( 'if sys.version_info[0] >2:')
        self.W.iappendnl( 1, 'from pandas.plotting import register_matplotlib_converters')
        self.W.iappendnl( 1, 'register_matplotlib_converters()')
        self.W.appendnl( 'matplotlib.style.use( "%s")\n' % ( _dviplot.get_property( 'colorscheme', 'ggplot')))
        self.W.appendnl( '')

        self._import_user_module()

        self.W.appendnl( KKPLOT_MATPLOTLIB_TIMEDELTA)
        self.W.appendnl( KKPLOT_MATPLOTLIB_TIMEPERIOD)
        self.W.appendnl( KKPLOT_MATPLOTLIB_ORTHOGONALPROJECTION)
        self.W.appendnl( KKPLOT_MATPLOTLIB_SORTBYZORDER)
        self.W.appendnl( '')

    def generate_postamble( self) :
        self.W.appendnl( '\n')
        self.W.appendnl( 'if __name__ == "__main__" :')
        self.W.iappendnl( 1, 'kkfigures, kkaxes = create_figure()\n')

    def _import_user_module( self) :
        self.W.iappendnl( 0, 'user_code_available = False')
## sk:off        import os
## sk:off
## sk:off        o = self.dviplot.outputfile.strip()
## sk:off        o = o.replace( '/', os.sep)
## sk:off        o = o.replace( '\\', os.sep)
## sk:off        o_path, o_file = os.path.split( o)
## sk:off        if not o_path == '' :
## sk:off            self.W.iappendnl( 0, 'import sys')
## sk:off            self.W.iappendnl( 0, 'sys.path.insert( 0, "%s")' % ( os.path.abspath( o_path)))
## sk:off        module_name = self._canonicalize_name( o_file)
## sk:off        self.W.iappendnl( 0, 'user_code_available = True')
## sk:off        self.W.iappendnl( 0, 'try:')
## sk:off        self.W.iappendnl( 1, 'import %s as user_code' % ( module_name))
## sk:off        self.W.iappendnl( 1, 'print( "seeing user changes, using them")')
## sk:off        self.W.iappendnl( 0, 'except ImportError : #as import_error :')
## sk:off        self.W.iappendnl( 1, '## no user code')
## sk:off        self.W.iappendnl( 1, '#print( "ImportError: %s" % ( import_error))')
## sk:off        self.W.iappendnl( 1, 'user_code_available = False')
## sk:off        self.W.iappendnl( 0, '')

    def _axis_index( self, _plot) :
        return '%s' % ( _plot.id)
    def _axis_position( self, _plot) :
        return '%s,%s' % ( _plot.position_y, _plot.position_x)


    def _canonicalize_name( self, _name) :
        validchars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789'
        canonicalized_name = ''
        for c in _name :
            if not c in validchars :
                canonicalized_name += '_'
            else :
                canonicalized_name += c

        return canonicalized_name

    def _make_args( self, _commas, **_kwargs) :
        args = ', '.join([ '%s=%s' % ( k, self._stringify( v)) for ( k, v) in zip( _kwargs.keys(), _kwargs.values()) if v is not None])
        if args == '' :
            pass
        elif _commas == 'l' :
            args = ', %s' % ( args)
        elif _commas == 'r' :
            args += ', '
        elif _commas == 'lr' or _commas == 'rl' :
            args = ', %s, ' % ( args)
        return args

    def _make_flabels( self, _columns, _graph, _kwargs) :
        dataframe = _kwargs.get( 'dataframe')
        if dataframe is None :
            return
        from kkplot.kkengines.pythoncode import fitness
        for column in _columns :
            lbl = self._make_label( column, _graph)
            if not lbl.strip().startswith( '@') :
                continue

            if not ':' in lbl :
                kklog_fatal( 'label format for functions "@F:arg1,arg2,...,argN"')

            lblfunc, lblargs = lbl.split( ':')
            lblfunc = lblfunc[1:]
            lblargs = lblargs.split( ',')

            fitness_fun = getattr( fitness, lblfunc)
            if not fitness_fun :
                kklog_fatal( 'unknown labeling function "%s"' % ( lblfunc))

            subcolumns = self._find_columns( lblargs, _columns)

            self.writer.push_indentlevel()
            lblvar = fitness_fun( self.writer, dataframe, subcolumns[0], subcolumns[1])
            self.writer.pop_indentlevel()

            fitness_fun_name = getattr( fitness, '%s_name' % ( lblfunc))
            if fitness_fun_name is None :
                kklog_fatal( 'no function called "%s_name"' % ( lblfunc))
            _graph.add_properties( { 'label.%s' % ( column): '<NOSTRINGIFY>"%s = %%0.2f" %% ( %s)' % ( fitness_fun_name(), lblvar)})

    def _make_label( self, _column, _graph) :
        lbl = lambda c : _graph.get_property( 'label.%s' % ( c))
        label = '%s' % ( '_nolabel' if lbl(_column) is None else lbl(_column))
        return label
    def _make_labels( self, _columns, _graph, **_kwargs) :
        if len( _kwargs) > 0 :
            self._make_flabels( _columns, _graph, _kwargs)
        labels = '%s' % ( ','.join( \
            [ '"%s":%s' % ( c, self._stringify( self._make_label(c,_graph))) for c in _columns]))
        return labels


    def _stringify( self, _value) :
        if _value is None :
            return 'None'
        elif type( _value) == str :
            if _value.startswith( '<NOSTRINGIFY>') :
                return '%s' % ( _value[13:]) ## TODO len( nostringify)
            return '"%s"' % ( _value)
        else :
            return '%s' % ( str( _value))

    def _toggle( self, _value) :
        kklog_debug( '%s->%s' % ( _value, not _value))
        if _value :
            return not _value
        return _value

    def _get_linestyle( self, _linestyle) :
        if _linestyle == 'solid' or _linestyle == 'line' or _linestyle == 'lines' :
            return '-'
        elif _linestyle == 'point' or _linestyle == 'points' :
            return 'None'
        elif _linestyle == 'dashdot' :
            return '-.'
        elif _linestyle == 'dashed' or _linestyle == 'dash' or _linestyle == 'dashes' :
            return '--'
        elif _linestyle == 'dotted' :
            return ':'

        kklog_warn( 'unsupported line style "%s"' % _linestyle)
        return '-'


__kkplot_engine_matplotlib_factory = kkplot_engine_matplotlib()

