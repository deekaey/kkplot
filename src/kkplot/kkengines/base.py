
from kkplot.kkutils.log import *

import sys

KKPLOT_ENGINES = dict()

class kkplot_plotmethod( object) :
    def __init__( self, _graph, _graphmethodcall) :
        self.graph = _graph
        self.methodcall = _graphmethodcall
    def __str__( self) :
        return 'graph <%s>, method=%s' % ( self.graph.graphid, self.methodcall)

class kkplot_engine( object) :
    def  __init__( self, _name, _conf, _dviplot) :
        self._name = _name
        self._conf = _conf
        self._dviplot = _dviplot

        self._plotmethods = dict()

        global KKPLOT_ENGINES
        if not self._name in KKPLOT_ENGINES :
            KKPLOT_ENGINES[self._name] = self

    def  help( self) :
        return  "no help available"
    def  generate( self) :
        sys.stderr.write( "method 'generate' not implemented\n")
        return  -1
    def  write( self) :
        sys.stderr.write( "method 'write' not implemented\n")

    def  __str__( self) :
        return  self.name;

    @property
    def  name( self) :
        return self._name
    @property
    def  config( self) :
        return self._conf
    @property
    def  dviplot( self) :
        return self._dviplot
    @property
    def  plotmethods( self) :
        return self._plotmethods
    def  add_plotmethods( self, _plotmethods) :
        self._plotmethods.update( _plotmethods)
    def  get_plotmethod( self, _graph) :
        plotmethodname = self.get_plotmethodname( _graph)
        if self._plotmethods.get( plotmethodname) is None :
            graph_kind, graph_projection = \
                self._get_plotmethodnamecomponents( _graph)
            kklog_warn( 'no plot method for plot kind "%s" using %s%s' \
                % ( graph_kind, _graph.domainkind, graph_projection))
            return None
        return self._plotmethods.get( plotmethodname)

    def get_plotmethodname( self, _graph) :
        plotmethodbasename, plotprojection = \
            self._get_plotmethodnamecomponents( _graph)
        return '%s_%s%s' % ( _graph.domainkind, plotmethodbasename, plotprojection)
    def _get_plotmethodnamecomponents( self, _graph) :
        graph_kind = _graph.get_property( 'kind', 'line')
        graph_projection = _graph.get_property( 'projection')

        if graph_projection is None or graph_projection == '' or graph_projection == '2d' :
            projection = ''
        elif graph_projection == '3d' :
            projection = '3d'
        else :
            kklog_warn( 'unknown projection  [projection=%s]' % ( graph_projection))
            raise RuntimeError( 'unknown projection')

        if graph_kind == 'standard' or graph_kind == 'line' or graph_kind == 'lines' :
            return ( 'line', projection)
        elif graph_kind == 'cumulativeline' :
            return ( 'cumulativeline', projection)
        elif graph_kind == 'fill' or graph_kind == 'fillbetween' or graph_kind == 'band' :
            return ( 'fill', projection)
        elif graph_kind == 'polygon' or graph_kind == 'polygons' :
            return ( 'polygons', projection)
        elif graph_kind == 'point' or graph_kind == 'points' :
            return ( 'points', projection)
        elif graph_kind == 'points+errors' :
            return ( 'points_errors', projection)
        elif graph_kind == 'bar' or graph_kind == 'bars' :
            return ( 'bars', projection)
        elif graph_kind == 'box' or graph_kind == 'boxes' or graph_kind == 'boxplot' or graph_kind == 'boxplots' :
            return ( 'boxes', projection)
        elif graph_kind == 'integratebar' or graph_kind == 'integrate+bar' :
            return ( 'integratebar', projection)
        elif graph_kind == 'area' or graph_kind == 'stack' or graph_kind == 'stacked' or graph_kind == 'stackedarea' :
            return ( 'area', projection)
        elif graph_kind == 'contour' :
            return ( 'contour', projection)
        elif graph_kind == 'raster' :
            return ( 'raster', projection)
        elif graph_kind == 'regressionline' :
            return ( 'regressionline', projection)
        elif graph_kind == 'regressionzero' or graph_kind == 'regression0' or graph_kind == 'regressionnointercept' :
            return ( 'regressionzero', projection)
        elif graph_kind == 'regressionpoint' :
            return ( 'regressionpoint', projection)
        elif graph_kind == 'heatmap' :
            return ( 'heatmap', projection)
        elif graph_kind == 'hist' or graph_kind == 'histogram' :
            return ( 'histogram', projection)

        elif graph_kind == 'pie' or graph_kind == 'piechart' :
            return ( 'pie', projection)

        elif graph_kind == 'shadebox' :
            return ( 'shadebox', projection)

        elif graph_kind == 'surface' :
            return ( 'surface', projection)

        elif graph_kind == 'bartable' :
            return ( 'bartable', projection)

        elif graph_kind == 'volume' :
            return ( 'volume', projection)
        else :
            #kklog_warn( 'unregistered graph type "%s"' % graph_kind)
            return ( graph_kind, projection)

        kklog_warn( 'unsupported graph type "%s"' % graph_kind)
        raise RuntimeError( 'unsupported graph type')


    def _generate_graphmethods( self, _graphmethodcall) :

        graphmethods = list()

        ## iterate graphs with their plots
        for graph, plot in self.dviplot :

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
                for ( column_id, column_name) in zip( column_ids, column_names) :
                    graph_label = graph.label( column_name)
                    if graph_label is None :
                        column_label = None
                    else :
                        column_label = '%s%s' % ( graph_label, graph.datalabel( dataselect, ' [%s]'))
                    graph.add_properties( { 'label.%s' % ( column_id): column_label})

            plotmethod = self.get_plotmethod( graph)
            if plotmethod and _graphmethodcall :
                graph_method_call = _graphmethodcall(
                    plotmethod, graph, plot, graph_columns, auxialiary_columns)
                if graph_method_call is None :
                    kklog_error( 'failed to generate code for graph "%s"' % ( graph.graphid))
                    return list()
                graphmethods.append( kkplot_plotmethod( graph, graph_method_call))
            else :
                pass

        return  graphmethods

    def _find_columns( self, _subcolumns, _columns) :
        subcolumns = []
        for subcolumn in _subcolumns :
            for column in _columns :
                if column.endswith( '.%s' % ( subcolumn)) :
                    subcolumns.append( column)
        return subcolumns


def  create( _name, _conf, _dviplot) :
    if _name in KKPLOT_ENGINES :
        kkengine = KKPLOT_ENGINES[_name].new( _conf, _dviplot)
        kklog_debug( 'using engine: %s' % ( kkengine))
        return  kkengine
    kklog_error( 'no such engine [%s] (available engines {%s})' % ( _name, ', '.join( KKPLOT_ENGINES.keys())))
    return  None

def  names() :
    return  KKPLOT_ENGINES.keys()

