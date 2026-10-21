
## example call
## python kkplot.py -E matplotlib examples/config.yml
##
## supported output formats:
##  eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff
##
## draws the figure directly from the in-memory data pool (no code generation)

from kkplot.kkengines.base import kkplot_engine as kkplot_engine
from kkplot.kkutils.log import *

from kkplot.kkengines.pythonmatplotlib.helpers import lit, kwargs, fixed, sort_by_zorder
from kkplot.kkengines.pythonmatplotlib.plotmethods import PLOTMETHODS, NODATA_PLOTMETHODS, COLUMNCHECKS

import sys
import types

class kkplot_engine_matplotlib( kkplot_engine) :
    generates_code = False

    def  __init__( self, _conf=None, _dviplot=None) :
        super( kkplot_engine_matplotlib, self).__init__( "matplotlib", _conf, _dviplot)
        self.add_plotmethods( PLOTMETHODS)

    def  new( self, _conf, _dviplot) :
        return  kkplot_engine_matplotlib( _conf, _dviplot)

    def  help( self) :
        return 'available graph types: { %s }' \
            % ( ', '.join( [ '\'%s\'' % ( plotmethod) for plotmethod in self.plotmethods]))

    def  write( self, _target=None) :
        pass

    def  generate( self) :
        graphs = self._collect_graphs()
        if graphs is None :
            return -1
        if len( graphs) == 0 :
            kklog_warn( 'nothing to plot')
            return -1
        if not self._conf.execute :
            kklog_info( 'not executing; no figure written')
            return 0

        import matplotlib
        matplotlib.use( 'Agg')
        import matplotlib.pyplot as pyplot
        from pandas.plotting import register_matplotlib_converters
        register_matplotlib_converters()
        matplotlib.style.use( self.dviplot.get_property( 'colorscheme', 'ggplot'))

        figure = pyplot.figure()
        axes = self._create_axes( figure, pyplot)
        self._draw_graphs( axes, graphs)

        for ax in axes.values() :
            if ax.get_gid() is None :
                figure.delaxes( ax)
        for plot in self.dviplot.plots :
            self._set_plot_properties( axes, plot)
        for plot in self.dviplot.plots :
            self._set_legend( axes[self._axis_index( plot)], plot)

        self._write_figure( figure)
        pyplot.close( figure)
        return 0

    def _axis_index( self, _plot) :
        return '%s' % ( _plot.id)

    def _collect_graphs( self) :
        """(graph, plot method, axes id, columns, auxiliary columns) for each graph"""
        graphs = list()
        for graph, plot in self.dviplot :
            if graph.domain is None :
                continue

            graph_columns = list()
            auxiliary_columns = list()
            datalabel = graph.get_property( 'datalabel', None)
            add_datalabel = graph.get_property( 'adddatalabel', True)
            for di, dataselect in enumerate( graph) :
                aux_column_ids = graph.referenceids( dataselect)
                column_id = []
                if len( aux_column_ids) > 0 :
                    column_id = aux_column_ids.pop( 0)
                graph_columns.append( column_id)
                auxiliary_columns.append( aux_column_ids)

                for ( column_id, column_name) in zip( graph.referenceids( dataselect), graph.names) :
                    graph_label = graph.label( column_name)
                    if type( datalabel) == list and di < len( datalabel) :
                        column_label = datalabel[di]
                    elif graph_label is None :
                        column_label = None
                    elif add_datalabel :
                        column_label = '%s%s' % ( graph_label, graph.datalabel( dataselect, ' [%s]'))
                    else :
                        column_label = '%s' % ( graph_label)
                    graph.add_properties( { 'label.%s' % ( column_id): column_label})

            plotmethod = self.get_plotmethod( graph)
            if plotmethod is None :
                continue
            if plotmethod in COLUMNCHECKS and COLUMNCHECKS[plotmethod]( graph_columns, auxiliary_columns) is None :
                kklog_error( 'failed to set up graph "%s"' % ( graph.graphid))
                return None

            ax_index = self._axis_index( plot)
            yaxisat = graph.get_property( 'yaxisat', 'left')
            if yaxisat == 'right' :
                ax_index += '.twin'
            elif yaxisat != 'left' :
                kklog_warn( 'graph property \'yaxisat\' has invalid value (%s); must be { %s, %s}' \
                    % ( yaxisat, 'left', 'right'))
            graphs.append( ( graph, plotmethod, ax_index, graph_columns, auxiliary_columns))

        return graphs

    def _create_axes( self, _figure, _pyplot) :
        axes = dict()
        for plot in self.dviplot.plots :
            ax_index = self._axis_index( plot)
            projection = plot.get_property( 'projection')
            ax = _pyplot.subplot2grid( ( self.dviplot.extent_y, self.dviplot.extent_x), \
                ( plot.position_y, plot.position_x), colspan=plot.span_x, rowspan=plot.span_y, fig=_figure, \
                **kwargs( projection=projection or None, facecolor=plot.get_property( 'backgroundcolor')))
            axes[ax_index] = ax
            if projection != '3d' and plot.get_property( 'twinx', True) :
                axes['%s.twin' % ( ax_index)] = ax.twinx()

            ax.ticklabel_format( useOffset=plot.get_property( 'ticklabelformat', False))

            axiscolor = plot.get_property( 'axiscolor', None)
            def set_spinecolor( _side) :
                color = plot.get_property( 'axiscolor%s' % ( _side), axiscolor)
                if color is not None :
                    ax.spines[_side].set_color( lit( '%s' % ( color)))

            set_spinecolor( 'bottom')
            ax.get_xaxis().set_visible( plot.get_property( 'xaxisvisible', True))
            ax.get_yaxis().set_visible( plot.get_property( 'yaxisvisible', True))

            ## broken axis marks
            marks = dict( marker=[ ( -1, -.25), ( 1, .25)], markersize=12, linestyle='none', \
                color='k', mec='k', mew=1, clip_on=False)
            for side, y in [ ( 'bottom', 0), ( 'top', 1)] :
                visible = plot.get_property( 'spines%svisible' % ( side), True)
                if not visible :
                    ax.spines[side].set_visible( visible)
                    ax.plot( [ 0, 1], [ y, y], transform=ax.transAxes, **marks)

            for side in [ 'top', 'right', 'left'] :
                set_spinecolor( side)

            axislinewidth = plot.get_property( 'axislinewidth', None)
            if axislinewidth is not None :
                for side in [ 'bottom', 'left', 'top', 'right'] :
                    ax.spines[side].set_linewidth( fixed( axislinewidth, '%.4f'))

        _figure.set_size_inches( fixed( self.dviplot.size_x), fixed( self.dviplot.size_y))
        return axes

    def _draw_graphs( self, _axes, _graphs) :
        context = types.SimpleNamespace( dviplot=self.dviplot, graphresults=dict())
        for graph, plotmethod, ax_index, columns, auxiliary_columns in _graphs :
            data = None
            if plotmethod not in NODATA_PLOTMETHODS :
                data = self.dviplot.series( graph.graphid, graph.domainkind)
                if data is None :
                    kklog_warn( 'no data for graph "%s"' % ( graph.graphid))
                    continue
            try :
                context.graphresults[graph.graphresult] = plotmethod( _axes[ax_index], \
                    graph, data, list( columns), [ list( aux) for aux in auxiliary_columns], context)
            except Exception as err :
                kklog_error( 'failed to create plot for graph "%s": %s: %s' \
                    % ( graph.graphid, type( err).__name__, err))

    def _set_plot_properties( self, _axes, _plot) :
        ax_index = self._axis_index( _plot)
        ax = _axes[ax_index]
        (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()

        def setprop( _props, _setter, _value=None, _bool=None, _twin=False) :
            values = list()
            for prop in _props.split( ',') :
                value = _plot.get_property( prop)
                if value is None or ( _bool is not None and value != _bool) :
                    return
                values.append( value if _value is None else _value)
            target = _axes.get( '%s.twin' % ( ax_index)) if _twin else ax
            if target is None :
                kklog_warn( 'plot "%s" has no right y-axis; ignoring "%s"' % ( ax_index, _props))
                return
            for attribute in _setter.split( '.') :
                target = getattr( target, attribute)
            target( *[ lit( value) for value in values])

        if _plot.get_property( 'bgcolor') is not None :
            kklog_warn( 'plot property "bgcolor" is not supported; use "backgroundcolor"')
        setprop( 'xlabel', 'set_xlabel')
        setprop( 'xlabelfontsize', 'xaxis.label.set_size')
        setprop( 'ylabel', 'set_ylabel')
        setprop( 'ylabelfontsize', 'yaxis.label.set_size')
        setprop( 'ylabelright', 'set_ylabel', _twin=True)
        setprop( 'ylabelrightfontsize', 'yaxis.label.set_size', _twin=True)
        setprop( 'zlabel', 'set_zlabel')

        if _plot.get_property( 'square', False) == True :
            setprop( 'square', 'set_aspect', abs( x1-x0) / abs( y1-y0))

        for ticks in [ 'xticks', 'yticks', 'xticklabels', 'yticklabels'] :
            value = _plot.get_property( ticks, False)
            if value is None or _plot.get_property( ticks) is False :
                getattr( ax, 'set_%s' % ( ticks))( [])
            elif isinstance( value, list) :
                if ticks.endswith( 'labels') :
                    value = [ '%s' % ( str( lbl)) for lbl in value ]
                getattr( ax, 'set_%s' % ( ticks))( value)

        for axis in [ 'x', 'y'] :
            rotation = _plot.get_property( '%sticklabelsrotation' % ( axis))
            if rotation is not None :
                for ticklabel in getattr( ax, 'get_%sticklabels' % ( axis))() :
                    ticklabel.set_rotation( rotation)

        setprop( 'grid', 'grid')
        setprop( 'align', 'axis', _value='tight', _bool=False)

        title = '' if _plot.title is None else _plot.title
        if _plot.get_property( 'titlepad', 0.0) > 0.0 :
            ax.set_title( lit( '%s' % ( title)), pad=fixed( _plot.get_property( 'titlepad')))
        else :
            ax.set_title( lit( title))

        xlow = _plot.get_property( 'xlimitlow', False)
        xhigh = _plot.get_property( 'xlimithigh', False)
        if ( type( xlow) == float and type( xhigh) == float) or \
           ( type( xlow) == int and type( xhigh) == int) or \
           ( isinstance( xlow, str) and isinstance( xhigh, str) and xlow != '' and xhigh != '') :
            try :
                ax.set_xlim( fixed( float( xlow)), fixed( float( xhigh)))
            except ValueError :
                try :
                    ax.set_xlim( lit( xlow), lit( xhigh))
                except Exception :
                    import matplotlib.dates as mdates
                    ax.set_xlim( mdates.datestr2num( lit( xlow)), mdates.datestr2num( lit( xhigh)))

        setprop( 'ylimitlow,ylimithigh', 'set_ylim')
        setprop( 'zlimitlow,zlimithigh', 'set_zlim')

    def _set_legend( self, _ax, _plot) :
        handles, labels = _ax.get_legend_handles_labels()
        if len( handles) == 0 :
            _ax.legend_ = None
            return
        handles, labels = sort_by_zorder( handles, labels)
        legend = _ax.legend( handles, labels, **kwargs(
            loc=_plot.get_property( 'legendlocation', 'best'),
            ncol=_plot.get_property( 'legendcolumns', 1),
            columnspacing=_plot.get_property( 'legendcolumnspacing'),
            fontsize=_plot.get_property( 'legendfontsize'),
            title=_plot.get_property( 'legendtitle')), frameon=False, fancybox=True, shadow=None)
        if _plot.get_property( 'legendtitlefontsize') and legend.get_title() :
            legend.get_title().set_fontsize( float( _plot.get_property( 'legendtitlefontsize')))
        legend.set_zorder( 10000)

    def _write_figure( self, _figure) :
        tl_left, tl_bottom, tl_right, tl_top = ( 0.0, 0.0, 1.0, 1.0)
        if self.dviplot.title :
            _figure.suptitle( lit( '%s' % ( self.dviplot.title)), fontsize=20)
            tl_top = 0.95
        tl_top = self.dviplot.get_property( 'tighttop', tl_top)

        outputfile = self.dviplot.outputpath
        sys.stderr.write( 'writing "%s"...\n' % ( outputfile))
        if self.dviplot.get_property( 'tight', True) == True :
            _figure.set_tight_layout( dict( rect=[ fixed( r, '%.2f') for r in ( tl_left, tl_bottom, tl_right, tl_top)]))
        if self.dviplot.get_property( 'padtop') is not None :
            _figure.subplots_adjust( top=0.85)
        _figure.savefig( outputfile, format=self.dviplot.outputfileformat, dpi=100.0, \
            transparent=False, pad_inches=0.1, facecolor='white')


__kkplot_engine_matplotlib_factory = kkplot_engine_matplotlib()
