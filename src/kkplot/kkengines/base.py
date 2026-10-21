
from kkplot.kkutils.log import *

import sys

KKPLOT_ENGINES = dict()

## graph kind (as written in plot file) -> plot method base name
KKPLOT_GRAPHKIND_ALIASES = {
    'standard': 'line', 'lines': 'line',
    'fillbetween': 'fill', 'band': 'fill',
    'polygon': 'polygons',
    'point': 'points',
    'points+errors': 'points_errors',
    'bar': 'bars',
    'box': 'boxes', 'boxplot': 'boxes', 'boxplots': 'boxes',
    'integrate+bar': 'integratebar',
    'stack': 'area', 'stacked': 'area', 'stackedarea': 'area',
    'regression0': 'regressionzero', 'regressionnointercept': 'regressionzero',
    'hist': 'histogram',
    'piechart': 'pie',
}

class kkplot_plotmethod( object) :
    def __init__( self, _graph, _graphmethodcall) :
        self.graph = _graph
        self.methodcall = _graphmethodcall
    def __str__( self) :
        return 'graph <%s>, method=%s' % ( self.graph.graphid, self.methodcall)

class kkplot_engine( object) :
    ## engines that generate code have it written (--bundle) and executed by kkplot
    generates_code = True

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

        ## unknown kinds are passed through unchanged
        return ( KKPLOT_GRAPHKIND_ALIASES.get( graph_kind, graph_kind), projection)


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


## engine name -> module that registers it on import
KKPLOT_ENGINE_MODULES = {
    'bokeh': 'kkplot.kkengines.pythonbokeh',
    'holoviews': 'kkplot.kkengines.pythonholoviews',
    'matplotlib': 'kkplot.kkengines.pythonmatplotlib',
    'tabular': 'kkplot.kkengines.pythontabular',
    'vtk': 'kkplot.kkengines.pythonvtk',
    'gnuplot': 'kkplot.kkengines.gnuplot',
    'null': 'kkplot.kkengines.null',
}

def  _load_engine( _name) :
    if _name not in KKPLOT_ENGINES and _name in KKPLOT_ENGINE_MODULES :
        import importlib
        try :
            importlib.import_module( KKPLOT_ENGINE_MODULES[_name])
        except ImportError as err :
            kklog_error( 'failed to load engine [%s]: %s' % ( _name, err))

def  create( _name, _conf, _dviplot) :
    _load_engine( _name)
    if _name in KKPLOT_ENGINES :
        kkengine = KKPLOT_ENGINES[_name].new( _conf, _dviplot)
        kklog_debug( 'using engine: %s' % ( kkengine))
        return  kkengine
    kklog_error( 'no such engine [%s] (available engines {%s})' % ( _name, ', '.join( names())))
    return  None

def  names() :
    return  KKPLOT_ENGINE_MODULES.keys()

