
import kkutils as utils
from kkutils.log import *
from kkutils.expand import *
from kkplot_figure import *
import kkplot_domains
import kkplot_provider

import yaml
import itertools
import sys

## http://stackoverflow.com/questions/7204805/dictionaries-of-dictionaries-merge
def merge_plotfiles( _a, _b):
    key = None
    kklog_debug( '%s to %s' %( _b, _a))
   
    #todo use consisten global variables for this in order to provide backward-compatibility with python 2.7
    if int(sys.version_info[0]) > 2:
        kkplot_long = int
        kkplot_unicode = str
    else:
        kkplot_long = long
        kkplot_unicode = unicode

    try:
        if _a is None or isinstance( _a, str) or isinstance( _a, kkplot_unicode) \
            or isinstance( _a, int) or isinstance( _a, kkplot_long) or isinstance( _a, float):
            # border case for first run or if _a is a primitive
            _a = _b
        elif isinstance( _a, list):
            # lists can be only appended
            if isinstance( _b, list):
                # merge lists
                _a.extend( _b)
            else:
                # append to list
                _a.append( _b)
        elif isinstance( _a, dict):
            # dicts must be merged
            if isinstance( _b, dict):
                for key in _b:
                    if key in _a:
                        _a[key] = merge_plotfiles( _a[key], _b[key])
                    else:
                        _a[key] = _b[key]
            else:
                raise yaml.YAMLError('Cannot merge non-dict "%s" into dict "%s"' % ( _b, _a))
        else:
            raise yaml.YAMLError('NOT IMPLEMENTED "%s" into "%s"' % ( _b, _a))
    except TypeError as typeerr:
        raise yaml.YAMLError('TypeError "%s" in key "%s" when merging "%s" into "%s"' % ( typeerr, key, _b, _a))
    return _a

class kkplot_pfreader_yaml( object) :
    def __init__( self, _conf, _pf_name) :
        self._conf = _conf
        self._pf_name = _pf_name
        self._pf_data = None

        self._figure = kkplot_figure()

        rc_load = self.load( self._pf_name)
        if rc_load :
            raise RuntimeError( 'loading config file failed')
        kklog_debug( 'loading plot configuration successful')

        rc_read = self.read()
        if rc_read :
            raise RuntimeError( 'reading config file failed')
        kklog_debug( 'reading plot configuration successful')

        self._engine = self._pf_data.get( 'engine')

    @property
    def plotfile( self) :
        return  self._pf_name

    @property
    def figure( self) :
        return  self._figure

    @property
    def engine( self) :
        return  self._engine

    def load( self, _fname, _mergewith=None) :
        rc_load = 0
        pf_stream = None
        yamldata = None
        try :
            try :
                if _fname == '-' :
                    pf_stream = sys.stdin
                else :
                    fname = kkexpand( _fname)
                    pf_stream = open( fname, 'r')
                try:
                    yamldata = yaml.load( pf_stream, Loader=yaml.FullLoader)
                except:
                    yamldata = yaml.load( pf_stream)
                if self._pf_data is None :
                    self._pf_data = yamldata
                else :
                    merge_plotfiles( self._pf_data, yamldata)
            except IOError as ioerr :
                kklog_error( '%s  [file=%s]' % ( ioerr, _fname))
                rc_load = -1
            except yaml.YAMLError as yaml_err :
                yaml_err_line = '?'
                yaml_err_col = '?'
                if hasattr( yaml_err, 'problem_mark') :
                    yaml_err_line = yaml_err.problem_mark.line+1
                    yaml_err_col = yaml_err.problem_mark.column+1
                kklog_error( '%s  [file=%s,line/column=%s/%s]' %
                        ( yaml_err, _fname, str(yaml_err_line), str(yaml_err_col)))
                rc_load = -1
        finally :
            if pf_stream :
                pf_stream.close()

        if yamldata :
            fincludes = yamldata.get( 'include')
            kklog_debug( 'includes=%s' % ( fincludes))
            if isinstance( fincludes, list) :
                for finclude in fincludes :
                    self.load( finclude)

        return  rc_load

    def read( self) :
        kklog_debug( 'reading plot configuration [%s]' % self._pf_name)

        self._figure, packed = self.read_figure()
        if self._figure is None :
            return -1

        if self.read_namedconstants() :
            return -1

        if self.read_plots( packed) :
            return -1

        return  0

    def read_figure( self) :
        fig = self._pf_data.get( 'figure')
        if fig :
            fig_title = fig.get( 'title', '')
            fig_title = kkexpand( fig_title)
            kklog_debug( 'figure title is "%s"' % ( fig_title))
            fig_output = fig.get( 'output', None)
            fig_output = kkexpand( fig_output)
            kklog_debug( 'figure output will be written to "%s"' % ( fig_output))
            fig_components = fig.get( 'components', False)
            if self._conf.components == "True" :
                    fig_components = True
        else :
            fig_title = None
            fig_output = None
        if fig :
            fig_output_format = fig.get( 'outputformat', None)
            kklog_debug( 'figure output format is "%s"' % ( fig_output_format))
        else :
            fig_output_format = None


        fig_props = fig.get( 'properties') if fig else None
        if fig_props is not None :
            fig_columns = fig_props.get( 'columns', 0)
            fig_width = fig_props.get( 'width', -1.0)
            fig_height = fig_props.get( 'height', -1.0)
            square = fig_props.get( 'square', False)
            pack_strategy = fig_props.get( 'packing', 'greedybestfit')
        else :
            fig_columns = 0
            fig_width = -1.0
            fig_height = -1.0
            square = False
            pack_strategy = 'greedybestfit'
        kklog_debug( 'packing strategy is "%s"' % ( pack_strategy))
        fig_rows, fig_columns, packed = \
                self.pack_plottiles( fig_columns, pack_strategy, fig_props )

        if fig_width < 0.0 :
            fig_width = 16.0 * fig_columns
        if fig_height < 0.0 :
            fig_height = 5.0 * fig_rows
        if square :
            fig_width = fig_height

        figure = kkplot_figure( _title=fig_title, _extent=( fig_rows, fig_columns), \
            _size=( fig_height, fig_width), _outputfile=fig_output, _outputfileformat=fig_output_format, _components=fig_components)

        figure.domain_time = self.read_domain( fig, \
            kkplot_domains.kkplot_domain_none(), kkplot_domains.kkplot_domain_time)
        figure.domain_space = self.read_domain( fig, \
            kkplot_domains.kkplot_domain_none(), kkplot_domains.kkplot_domain_space)
        if self._is_valid( fig, 'datasource') :
            figure.datasource = \
                self.read_source( fig['datasource'], kkplot_datasource())

        if self._is_valid( fig, 'style') :
            figure.add_properties( fig['style'])
        if self._is_valid( fig, 'properties') :
            figure.add_properties( fig['properties'])

        return figure, packed

    def pack_plottiles( self, _columns, _strategy=None, _figure_properties=None) :
        sort_extents = True
        if _strategy == 'static':
            sort_extents = False
        n_tiles, extents = self.get_number_of_tiles( sort_extents)
        min_rows, min_cols = max( [ e[1] for e in extents ] ), max( [ e[2] for e in extents ] )
        kklog_debug( 'extents: ' + str( extents ) + '  min (rows/cols): '+str(min_rows)+'/'+str(min_cols) )
        packed = None
        while packed is None :
            R, C = self.get_extent( n_tiles, _columns, _min_rows=min_rows, _min_cols=min_cols)
            _R, _C, packed = utils.pack( R, C, extents, _strategy, self.get_alignment( _figure_properties))
            n_tiles += 1
        for p, ( m, n, r, c ) in zip( packed.keys(), packed.values() ) :
            packed[p] = ( ( r, c ), ( m, n ) )
        kklog_debug( 'packing: ' + str( packed ) )
        #print _R, _C
        return _R, _C, packed

## FIXME  check plot for exclusively hidden graphs (move to separate module)
    def get_extent( self, _n_tiles, _columns, _min_rows, _min_cols) :
        if _columns < 1 :
            rows, columns = self.auto_layout(
                _n_tiles, _min_rows=_min_rows, _min_cols=_min_cols)
        else :
            columns = _columns
            rows = int( _n_tiles / columns)
            if ( rows * columns) < _n_tiles :
                rows += 1
        return ( rows, columns)

    def auto_layout( self, _n_tiles, _min_rows, _min_cols) :
        M, N = utils.auto_layout( _n_tiles, _min_rows, _min_cols)
        kklog_debug( 'auto-layout= %d,%d for %d tiles' % ( M, N, _n_tiles))
        return M, N

    def get_number_of_tiles( self, _sort_extents=True) :
        n_tiles = 0
        extents = list()
        for plot_k in self._pf_data['plots'] :

            plot_id = list(plot_k.keys())[0]
            if not self._is_valid_id( "plotID", plot_id) :
                return  -1
            plot_block = plot_k[plot_id]

            r, c = ( 1, 1) ## ( row, column ) span
            if plot_block.get( 'span') is not None :
                r, c = ( plot_block['span'][0], plot_block['span'][1])
            extents.append( ( plot_id, r, c ) )
            n_tiles += r * c

        if _sort_extents :
            ## sort extents by size (descending) and keep plot position within size group
            grouped_extents = dict()
            for j, r, c in extents :
                s = r * c
                if s not in grouped_extents :
                    grouped_extents[s] = list()
                grouped_extents[s].append( ( j, r, c ) )
            extents = list()
            for s in sorted( grouped_extents.keys(), reverse=True) :
                extents += grouped_extents[s]
        return n_tiles, extents

    def get_alignment( self, _figure_properties=None) :
        if _figure_properties :
            if 'alignmentorder' in _figure_properties :
                return _figure_properties['alignmentorder']
        return 'columnsfirstdownward'

    def read_namedconstants( self) :
        if self._is_valid( self._pf_data, 'define') :
            self._figure.add_defines( self._pf_data['define'])
        return 0

    def read_plots( self, _packed) :
        if len( self._pf_data.get( 'plots', [] )) == 0 :
            return 0

        plot_info_defaults = { 'datasource':self._figure.datasource }
        for plot_k in self._pf_data['plots'] :

            plot_id = list(plot_k.keys())[0]
            if not self._is_valid_id( "plotID", plot_id) :
                return  -1
            plot_block = plot_k[plot_id]

            plot_title = plot_block.get( 'title')
            plot_infos = self.read_graph_infos( plot_block, plot_info_defaults)

            graph_info_defaults = { 'datasource':plot_infos['datasource'] }
            graphs_tag = 'graphs'
            if not graphs_tag in plot_block.keys() :
                graphs_tag = 'compounds'
            if not graphs_tag in plot_block.keys() :
                kklog_error( 'plot requires at least 1 \'graph\' (or \'compound\' (deprecated))')
                return -1

            pos, span = _packed[plot_id]

            new_plot = kkplot_plot( _id=plot_id, _title=plot_title, _pos=pos, _span=span)
            new_plot.set_domain( self.read_domain( plot_block, self._figure.domain))

            new_plot.add_properties( self._figure.properties)
            if plot_block.get( 'style') is not None :
                new_plot.add_properties( plot_block['style'])
            if plot_block.get( 'properties') is not None :
                new_plot.add_properties( plot_block['properties'])

            for j, graph_id in enumerate( plot_block[graphs_tag]) :

                kklog_debug( '\n[%02d] graph-id=%s (%s)\n' % ( j, graph_id, type(graph_id)))
                ## FIXME  this still allows invalid syntax
                graphs_block = plot_block[graphs_tag]
                if isinstance( graph_id, str) :
                    pass
                elif isinstance( graph_id, dict) :
                    graph_id = list(graph_id.keys())[0] if len( list(graph_id.keys())) > 0 else None
                    graphs_block = graphs_block[j]
                else :
                    pass
                if graph_id is None :
                    kklog_error( 'invalid graph ID')
                    return -1
                if not self._is_valid_id( "graphID", graph_id) :
                    return  -1

                graph_block = graphs_block[graph_id]

                graph_names = [ graph_id]
                graph_labels = None

                if graph_block is not None :
                    if 'name' in graph_block :
                        graph_names = graph_block['name']
                        if graph_names is None :
                            graph_names = [ ':none:']
                        elif type( graph_names) == list :
                            graph_names = [ gn.strip() for gn in graph_names]
                        else :
                            graph_names = [ graph_names.strip()]

                    if 'label' in graph_block :
                        graph_labels = graph_block['label']
                        if graph_labels is None :
                            graph_labels = ':none:'

                graph_infos = \
                    self.read_graph_infos( graph_block, graph_info_defaults)

                new_graph = kkplot_graph( graph_id, graph_names, \
                    graph_labels, plot_id)
                new_graph.add_properties( { '@index':j, 'index':j})
                new_graph.set_domain( self.read_domain( graph_block, new_plot.domain))

                if self._is_valid( graph_block, 'groupby') :
                    graph_groupby = graph_block['groupby']
                    for k, group in enumerate( graph_groupby) :
                        if len( group) != 1 :
                            kklog_error( 'exactly one entry required in groupby block  [graph=%s]' % ( new_graph.graphid))
                            return -1
                        group0 = list(group.keys())[0]
                        if group.get( group0) is not None :
                            new_graph.add_group( group0, group.get( group0))
                        else :
                            kklog_error( 'group without criteria  [graph=%s]' % ( new_graph.graphid))
                            return -1

                if new_graph.name is not None :
                    graph_datasource = graph_infos['datasource']
                    for terminal in new_graph.terminals :
                        datasource = None
                        terminal_with_source = [ s.strip() for s in terminal.split( DSSEP)]
                        if len( terminal_with_source) == 1 :
                            datasource = graph_datasource
                        elif len( terminal_with_source) == 2 :
                            kklog_debug( 'reading datasource information for terminal "%s"' % ( terminal))
                            datasource = self.read_source( \
                                terminal_with_source[1], graph_datasource)
                        else :
                            kklog_error( 'invalid column specification  [column=%s]' % ( terminal))
                            return -1
                        if datasource is None :
                            return -1
                        new_graph.add_datasource( terminal, datasource)

                new_graph.add_properties( new_plot.properties)
                if self._is_valid( graph_block, 'style') :
                    new_graph.add_properties( graph_block['style'])
                if self._is_valid( graph_block, 'properties') :
                    new_graph.add_properties( graph_block['properties'])

                new_plot.append_graph( graph_id, new_graph)

            self._figure.append_plot( plot_id, new_plot)

        return  0

    def read_domain( self, _node, _default, _domainclass=None) :
        if _domainclass is not None :
            domainkind = _domainclass().kind
            if self._is_valid( _node, domainkind) :
                return _domainclass( _node[domainkind])
        else :
            if self._is_valid( _node, 'time') :
                return kkplot_domains.kkplot_domain_time( _node['time'])
            elif self._is_valid( _node, 'space') :
                return kkplot_domains.kkplot_domain_space( _node['space'])
            elif 'domain' in _node :
                domainnode = _node['domain']
                if domainnode is None or domainnode.get( 'kind') is None or domainnode.get( 'kind') == 'none' :
                    return kkplot_domains.kkplot_domain_none( _node.get( 'none'))
                elif domainnode['kind'] == 'time' or domainnode['kind'] == 'space' :
                    return self.read_domain( domainnode, _default)
                else :
                    kklog_warn( 'domain kind not understood  [domain=%s]' % ( domainnode['kind']))
                    return _default
            else :
                pass
        return _default



    def read_graph_infos( self, _node, _defaults) :
        plot_source = _defaults['datasource']
        if _node and 'datasource' in _node.keys() :
            plot_source = self.read_source( \
                _node['datasource'], _defaults['datasource'])
        return { 'datasource':plot_source }

    def read_source( self, _source, _refsource) :
        if not _source :
            return  kkplot_datasource( '%s' % ( _refsource.name))
        if type( _source) is dict :
            return  self._read_source( _source, _refsource)
        elif type( _source) is str :
            if not self._is_valid_id( "datasourceID", _source) :
                return  None
            sources = self._pf_data['datasources']
            if not sources :
                return  None
            source = sources.get( _source)
            if not source :
                kklog_error( 'no such source block  [datasource=%s]' % ( _source))
                return  None

            return  self._read_source( source, _refsource)

        else :
            kklog_error( 'i do not know what kind of datasource i am looking at')
            return  None

    def _read_source( self, _source, _refsource) :
        new_source = kkplot_datasource( '%s' % ( self._get_source_name( _source)))

        if self._is_valid( _source, 'kind') :
            new_source.kind = _source['kind']
        else :
            new_source.kind = _refsource.kind

        if self._is_valid( _source, 'format') :
            new_source.format = _source['format']
        else :
            new_source.format = _refsource.format
        new_source.add_formatargs( _refsource.formatargs)
        new_source.add_formatargs( _source.get( 'formatargs'))

        if self._is_valid( _source, 'flavor') :
            new_source.flavor = _source['flavor']
        else :
            new_source.flavor = _refsource.flavor
        new_source.add_flavorargs( _refsource.flavorargs)
        new_source.add_flavorargs( _source.get( 'flavorargs'))

        if self._is_valid( _source, 'path') :
            new_source.set_path( _source['path'], self._conf.base_dir_for( new_source.kind))
        else :
            new_source.set_path( _refsource.path)

        if self._is_valid( _source, 'provider') :
            s_provider = _source['provider']
            if self._is_valid( s_provider, 'program') :
                p_program = s_provider['program']
            else :
                p_program = None
            if self._is_valid( s_provider, 'arguments') :
                p_arguments = s_provider['arguments']
            else :
                p_arguments = None
            new_provider = kkplot_provider.kkplot_provider( \
                p_program, p_arguments, self._conf.base_dir_for( 'providers'))
            new_source.provider = new_provider

        kklog_debug( new_source)
        return  new_source

    def _get_source_name( self, _source) :
        source_id = id( _source)
        sources = self._pf_data['datasources']
        if not sources :
            return source_id
        for source in sources :
            if id( sources[source]) == source_id :
                return source
        return ':%s:' % ( str( source_id))

    def _is_valid( self, _node, _tag) :
        return _node and _node.get( _tag) is not None

    def _is_valid_id( self, _id_kind, _id) :
        validchars_ID = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789'
        invalid_chars = list()
        nb_invalid_chars = 0
        for c in _id :
            if c not in validchars_ID :
                nb_invalid_chars += 1
                if c not in invalid_chars :
                    invalid_chars.append( c)
        if len( invalid_chars) != 0 :
            kklog_error( '%s "%s" contains %d invalid character(s): %s' \
                % ( _id_kind, _id, nb_invalid_chars, ''.join(invalid_chars)))
            return  False
        return  True

