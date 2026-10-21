
from kkplot.kkutils.log import *
from kkplot.kkutils.timedelta import parse_timedelta
from kkplot.kkplot_pfyaml import kkplot_pfreader_yaml as pfreader_yaml
from kkplot.kkplot_figure import kkplot_figure as kkplot_figure
from kkplot.kkplot_figure import isreference as kkplot_isreference
from kkplot.kkplot_figure import asname as kkplot_asname
from kkplot.kkplot_figure import nocolumndepends as kkplot_nocolumndepends

from kkplot.kksources import kkplot_sourcefactory as kkplot_sourcefactory

import sys
import os as os
import warnings
import pandas as pandas
import numpy as numpy
import numexpr as numexpr
from datetime import datetime

import re
def canonicalize_name( _name) :
    return re.sub( '[^A-Za-z0-9_]', '_', _name.strip( ' \t./\\'))

def timestamp(_y,_m,_d):
    return datetime.strptime( str(_y)+"-"+str(_m)+"-"+str(_d), '%Y-%m-%d')

def timeperiod(_y1,_m1,_d1,_y2,_m2,_d2,_res='day'):
    start = datetime.strptime( str(_y1)+"-"+str(_m1)+"-"+str(_d1), '%Y-%m-%d')
    end = datetime.strptime( str(_y2)+"-"+str(_m2)+"-"+str(_d2), '%Y-%m-%d')
    delta = end-start
    return delta.days

## resampling functions usable in plot file expressions:
##   {day,week,month,year}{sum,max,mean,std}( column, n=1)
## pandas >= 2.2 renamed month/year end aliases 'M'/'A' to 'ME'/'YE'
_pandas_new_aliases = tuple( int( v) for v in pandas.__version__.split( '.')[:2]) >= ( 2, 2)
KKPLOT_RESAMPLE_FREQUENCIES = dict(
    day='D', week='W-MON',
    month='ME' if _pandas_new_aliases else 'M',
    year='YE' if _pandas_new_aliases else 'A')

def _make_resampler( _freq, _aggregate) :
    def resampler( _dataframe, _nd=1) :
        return getattr( _dataframe.resample( '%d%s' % ( _nd, _freq)), _aggregate)()
    return resampler

for _period, _freq in KKPLOT_RESAMPLE_FREQUENCIES.items() :
    for _aggregate in [ 'sum', 'max', 'mean', 'std'] :
        globals()[_period+_aggregate] = _make_resampler( _freq, _aggregate)

def cumsum( _dataframe) :
    return _dataframe.cumsum()

def custom_nansum(arr):
    if numpy.all(numpy.isnan(arr)):
        return numpy.nan
    else:
        return numpy.nansum(arr)

def nansum( _dataframe_1, _dataframe_2, *_dataframes) :
    #index = _dataframe_1.index 
    #series = pandas.Series( numpy.nansum( [ _dataframe_1, _dataframe_2 ] + list( _dataframes), axis=0))
    #series.index = index
    return pandas.concat([ _dataframe_1, _dataframe_2 ] + list( _dataframes), axis=1).apply(custom_nansum, axis=1)

def nanmean( _dataframe_1, _dataframe_2, *_dataframes) :
    index = _dataframe_1.index 
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        series = pandas.Series( numpy.nanmean( [ _dataframe_1, _dataframe_2 ] + list( _dataframes), axis=0))
        series.index = index
    return series

def nanstd( _dataframe_1, _dataframe_2, *_dataframes) :
    index = _dataframe_1.index 
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        series = pandas.Series( numpy.nanstd( [ _dataframe_1, _dataframe_2 ] + list( _dataframes), axis=0))
        series.index = index
    return series

def nanmin( _dataframe_1, _val) :
    index = _dataframe_1.index
    series = pandas.Series( numpy.min( [_dataframe_1, [_val for i in range(len(_dataframe_1))]], axis=0))
    series.index = index
    return series

def nanmax( _dataframe_1, _val) :
    index = _dataframe_1.index
    series = pandas.Series( numpy.max( [_dataframe_1, [_val for i in range(len(_dataframe_1))]], axis=0))
    series.index = index
    return series

def kkround( _dataframe, _decimals) :
    return numpy.round(_dataframe, _decimals)

def diff( _dataframe) :
    return _dataframe.diff()

from scipy import integrate
_trapezoid = getattr( integrate, 'trapezoid', None) or integrate.trapz

## time-weighted mean of the series scaled to _timeperiod (default: covered
## days); with _error, the root mean square instead (error propagation).
## returns a single value placed at the last time stamp (or _timestamp).
def integral( _dataframe, _timeperiod=None, _timestamp=None, _error=0) :
    data_clean = _dataframe.dropna()
    index = data_clean.index
    seconds = ( index - index[0]).total_seconds()
    time_scale = _timeperiod if _timeperiod else ( index[-1] - index[0]).days

    if _error == 0 :
        value = _trapezoid( data_clean, seconds) / seconds[-1] * time_scale
    else :
        value = ( _trapezoid( data_clean**2.0, seconds) / seconds[-1])**0.5 * time_scale

    stamp = _timestamp if _timestamp else index[-1]
    return pandas.Series( [ value], index=pandas.DatetimeIndex( [ stamp], name=index.name), name=data_clean.name)


class kkplot_dviplot( object) :
    def __init__( self, _conf, _pf_name, _pf_format='yaml') :

        self._conf = _conf
        self._engine = _conf.engine
        self._figure = kkplot_figure()
        if _pf_format == 'yaml' :
            pf_reader = pfreader_yaml( _conf, _pf_name)
            self._figure = pf_reader.figure
            if self._engine is None :
                self._engine = pf_reader.engine

        self._outputfile = _conf.output
        if self._outputfile is None :
            self._outputfile = self._figure.outputfile
        self._outputfileformat = _conf.outputformat
        if self._outputfileformat is None :
            self._outputfileformat = self._figure.outputfileformat

        toposorted_entities, self._toposorted_graphs = self._figure.prepare()
        series = dict()
        if not self._conf.skip_data_collection :
            terminal_readermap = self._construct_entity_readers( toposorted_entities)
            series = self._merge_data( toposorted_entities, terminal_readermap)
            if series is None :
                kklog_fatal( 'failed to read entity from datasource')
            series = self._evaluate_domain_expressions( series, toposorted_entities)
            series = self._delete_terminal_columns( series)
            ## the matplotlib engine plots from memory
            if self._engine != 'matplotlib' or self._conf.bundle :
                self._write_data( series)

        self._seriesids = series.keys()
        self._series = series

    def series_exists( self, _serieid) :
        return _serieid in self._seriesids

    def series( self, _serieid, _kind='time') :
        """data pool shaped like it is read back from the file written
        by _write_data (extra 'row' column, time index in seconds)"""
        serie = self._series.get( _serieid)
        if serie is None or serie.empty :
            return None
        serie = serie.dropna( how='all').reset_index()
        serie.insert( 0, 'row', range( len( serie)))
        if _kind == 'time' :
            if 'time' not in serie.columns :
                return None
            time = pandas.to_datetime( serie['time'])
            if time.dt.tz is not None :
                time = time.dt.tz_localize( None)
            serie['time'] = time.dt.floor( 's').astype( 'datetime64[ns]')
            serie = serie.set_index( serie.columns[1])
        return serie

    @property
    def series_kinds( self) :
        return  [ 'time', 'space', 'non']

    @property
    def plotfile( self) :
        return  self._pf_name

    @property
    def extent_x( self) :
        return self._figure.columns
    @property
    def extent_y( self) :
        return self._figure.rows

    @property
    def size_x( self) :
        return self._figure.width
    @property
    def size_y( self) :
        return self._figure.height
    def get_property( self, _property, _default=None) :
        return self._figure.get_property( _property, _default)

    @property
    def groupbytag( self) :
        return self._figure.groupbytag

    @property
    def engine( self) :
        return self._engine

    @property
    def title( self) :
        return self._figure.title

    @property
    def components( self) :
        return self._conf.components

    @property
    def outputfile( self) :
        of = self._outputfile
        if not os.path.isabs( of) :
            of = '%s/%s' % ( self._conf.outputs_dir(), of)
        if self._conf.bundle :
            of = of if of.rfind( os.sep) == -1 else of[of.rfind( os.sep)+1:]
        return  of
    @property
    def outputpath( self) :
        of = self._outputfile
        if not os.path.isabs( of) :
            of = '%s/%s' % ( self._conf.outputs_dir(), of)
        return  of
    @property
    def outputfileformat( self) :
        return self._outputfileformat

    @property
    def output_basename( self) :
        of = self._outputfile
        of = of if of.rfind( os.sep) == -1 else of[of.rfind( os.sep)+1:]
        of = of if of.rfind( "/") == -1 else of[of.rfind( "/")+1:]
        of = of if of.rfind( '.') == -1 else of[:of.rfind( '.')]
        return  of

    @property
    def output_directory( self) :
        if self._conf.bundle :
            output_dir = self.output_basename
            output_dir = '%s/%s.dir/' % ( self._conf.outputs_dir(), output_dir)
        else :
            output_dir = '%s' % ( self._conf.tmp_dir())
        return  output_dir

    def create_output_directory( self) :
        output_dir = self.output_directory
        if not os.path.exists( output_dir) :
            os.makedirs( output_dir)
            if not os.path.exists( output_dir) :
                return  None
        return  output_dir

    def datapool_filename( self, _serieid, _abs=False) :
        fn = '%s-%s.%s' % ( self.output_basename, \
                canonicalize_name( _serieid), 'csv')
        if _abs or not self._conf.bundle :
            output_dir = self.output_directory
            fn = '%s/%s' % ( output_dir, fn)
        return fn

    def source_filename( self, _suffix) :
        fp = self.output_directory
        fn = self.output_basename
        return '%s/%s.%s' % ( fp, fn, _suffix)

    def __iter__( self) :
        for graph in self._toposorted_graphs :
            yield ( graph, graph._plot)
    @property
    def plots( self) :
        return [ plot for plot in self._figure ]

    def _construct_entity_readers( self, _entities) :
        entity_readermap = dict()
        for entity in _entities :
            graph = self._figure.get_graph( entity)
            kklog_debug( 'read %s' % entity)
            kklog_debug( '  deps=%s' % graph.dependencies( entity))
            kklog_debug( '  expr=%s' % graph.expression( entity))

            for dependency in graph.dependencies( entity) :
                if not kkplot_isreference( dependency) :
                    datasource = graph.get_datasource( dependency)
                    kklog_debug( '  source=%s' % ( datasource.path))
                    kklog_debug( '    source me "%s"' % ( dependency))
                    if datasource.name in entity_readermap :
                        kklog_debug( 'already loaded source [%s]' % ( datasource.name))
                        continue
                    entity_reader = self._construct_entity_reader( dependency, datasource)
                    if entity_reader is None :
                        raise RuntimeError( '')
                    entity_readermap[datasource.name] = entity_reader

        return entity_readermap

    def _construct_entity_reader( self, _entity, _datasource) :
        if _datasource is None or _datasource.path is None :
            raise RuntimeError( 'data source not set for entity "%s"' % ( _entity))

        entity_reader_constructor = kkplot_sourcefactory( _datasource, self._conf)
        kklog_debug( 'dviplot datasource flavor "%s" (%s)' % ( _datasource.flavor, _datasource.flavorargs))
        entity_reader = entity_reader_constructor.construct()
        if entity_reader is None :
            raise IOError( 'failed to read data source  [%s]' % ( _datasource.name))
        kklog_debug( 'loaded source [%s]' % ( _datasource.name))
        return entity_reader

    def _merge_data( self, _entities, _entity_readermap) :
        series = dict()
        for entity in _entities :
            graph = self._figure.get_graph( entity)
            if series.get( graph.graphid) is None :
                series[graph.graphid] = pandas.DataFrame()

            for dependency in graph.dependencies( entity) :
                if kkplot_isreference( dependency) :
                    continue

                datasource = graph.get_datasource( dependency)
                series_kind = graph.domainkind

                entity_reader = _entity_readermap[datasource.name]

                queryname = kkplot_asname( dependency)
                for dataselect in graph :
                    targetname = graph.dataid( dataselect, dependency)
                    if targetname in series[graph.graphid].columns :
                        kklog_debug( 'datacolumn "%s" for graph "%s" exists. skipping.' % ( targetname, graph.graphid))
                        continue
        
                    selected_data = pandas.DataFrame()
                    if graph.name is None :
                        pass
                    else :
                        selected_data = entity_reader.read( graph, [queryname], [targetname], dataselect)
                        if selected_data is None :
                            return None

                    if selected_data.empty :
                        kklog_warn( 'no data for graph  [graph=%s,datalabel=%s]' % ( graph.graphid, graph.datalabel( dataselect)))
                    else :
                        series[graph.graphid] = self._merge_data_join_series( graph.graphid, \
                            series_kind, series[graph.graphid], selected_data, \
                            graph.domain.domaincolumns, datasource)

        return series

    def _merge_data_join_series( self, _graphid, _kind, _series_pool, _series, _index_columns, _datasource) :
        if _kind == 'time' :
            return self._merge_data_join_timeseries( _series_pool, _series, _index_columns, _datasource)
        elif _kind == 'space' :
            return self._merge_data_join_spaceseries( _series_pool, _series, _index_columns, _datasource)
        elif _kind == 'non' :
            return self._merge_data_join_nonseries( _series_pool, _series)
        else :
            kklog_fatal( 'unknown series kind [kind=%s]' % ( _kind))
        return None
    def _merge_data_join_nonseries( self, _nonseries_pool, _nonseries) :
        for column in _nonseries.columns :
            _nonseries_pool[column] = _nonseries[column]
        return _nonseries_pool
    def _merge_data_join_timeseries( self, _timeseries_pool, _timeseries, _index_columns, _datasource) :
        timeseries = self._transform_domaincolumns_time( _timeseries, _index_columns, _datasource)
        timeseries = timeseries.set_index( _index_columns)
        timeseries.dropna(axis=0, how='all', inplace=True)
        _timeseries_pool.dropna(axis=0, how='all', inplace=True)
        try:
            return pandas.concat( [_timeseries_pool, timeseries], axis=1, join='outer')
        except:
            duplicated_indexes_pool = timeseries.index[_timeseries_pool.index.duplicated()]
            if len(duplicated_indexes_pool) > 0:
                print("Duplicated indeces:")
                print(duplicated_indexes_pool)
                
            duplicated_indexes_timeseries = timeseries.index[timeseries.index.duplicated()]
            if len(duplicated_indexes_timeseries) > 0:
                print("Duplicated indeces:")
                print(duplicated_indexes_timeseries)
            return None
    def _merge_data_join_spaceseries( self, _spaceseries_pool, _spaceseries, _index_columns, _datasource) :
        spaceseries = _spaceseries.set_index( _index_columns)
        timeseries = self._transform_domaincolumns_space( timeseries, _datasource)
        return pandas.concat( [_spaceseries_pool, spaceseries], axis=1, join='outer')

    def _transform_domaincolumns_time( self, _timeseries, _index_columns, _datasource) :
        t_shiftarg = _datasource.flavorarg( 'shift')
        if t_shiftarg is not None :
            t_shift = parse_timedelta( t_shiftarg)
            if t_shift is not None :
                kklog_verbose( 'time-shifting data "%s" by [%s]' % ( _datasource.name, t_shift))
                _timeseries[_index_columns] += pandas.to_timedelta( t_shift)
        return  _timeseries
    def _transform_domaincolumns_space( self, _spaceseries, _datasource) :
        t_shiftarg = _datasource.flavorarg( 'shift')
        if t_shiftarg is not None :
            kklog_warn( 'missing implementation for space shift')
        return  _spaceseries


    def _evaluate_domain_expressions( self, _series, _entities) :
        entities = list([ entity for entity in _entities])
        series = dict()
        for entity in entities :
            #kklog_debug( 'entity="%s"' % ( entity))
            if kkplot_nocolumndepends( entity) :
                continue
            graph = self._figure.get_graph( entity)
            serie = _series.get( graph.graphid, None)
            if serie is None :
                kklog_fatal( 'missing data for entity  [entity=%s]' % ( entity))
            series[graph.graphid] = self._evaluate_expressions( _series, entity, graph)
        return series


    def _evaluate_expressions(self, _series, _entity, _graph):
        for dataselect in _graph:
            entity_assign, expression = self._rewrite_expression(_series, _entity, _graph, dataselect)

            try:
                add = pandas.Series(eval(expression), name=entity_assign)
            except Exception:
                add = pandas.Series(
                    [numpy.nan for i in range(len(_series[_graph.graphid]))],
                    name=entity_assign
                )

            try:
                _series[_graph.graphid] = pandas.concat(
                    [_series[_graph.graphid], add],
                    axis=1,
                    join='outer'
                )

            except pandas.errors.InvalidIndexError as e:
                df = _series[_graph.graphid]

                print("InvalidIndexError during concat")
                print(f"graphid: {_graph.graphid}")
                print(f"entity_assign: {entity_assign}")
                print(f"expression: {expression}")
                print()

                print("Left object type:", type(df))
                print("Right object type:", type(add))
                print()

                print("Left index unique:", df.index.is_unique)
                if not df.index.is_unique:
                    dup_left_idx = df.index[df.index.duplicated()].unique()
                    print("Duplicate left index values:")
                    print(list(dup_left_idx))

                print("Right index unique:", add.index.is_unique)
                if not add.index.is_unique:
                    dup_right_idx = add.index[add.index.duplicated()].unique()
                    print("Duplicate right index values:")
                    print(list(dup_right_idx))

                if hasattr(df, "columns"):
                    print("Left columns unique:", df.columns.is_unique)
                    if not df.columns.is_unique:
                        dup_left_cols = df.columns[df.columns.duplicated()].unique()
                        print("Duplicate left column names:")
                        print(list(dup_left_cols))

                print("Right series name:", add.name)
                if hasattr(df, "columns") and add.name in df.columns:
                    print(f"Right series name already exists in left columns: {add.name}")

                raise

        return _series[_graph.graphid]

    def _rewrite_expression( self, _series, _entity, _graph, _dataselect) :
        expression = _graph.expression( _entity)
        #kklog_info( '%s = %s' % ( _graph.graphid, expression))
        dependencies = list( _graph.dependencies( _entity))
        ## sort by string length (descending) to disambiguate
        #dependencies.sort( lambda d1, d2: cmp( len(d2), len(d1)))
        dependencies.sort( key=len)

        dataselect_index = _graph.asindex( _dataselect)
        if dataselect_index != '' :
            dataselect_index = '%s%s' % ( self.groupbytag, dataselect_index)

        entity_assign = '%s%s' % ( _entity, dataselect_index)
        #kklog_debug( 'entity_assign= "%s" + "%s"' % ( _entity, dataselect_index))

        rewrite_expression = expression

        #sort list in order to start with longest string to avoid substring replacement
        #[val_a@src_ab, val_ab@src_ab] # replacing first  val_a would affect val_ab as well
        for dependency in sorted(dependencies, key=len, reverse=True) :
            dependency_name = _graph.dataid( _dataselect, dependency)
            graph = self._figure.get_graph( dependency_name)

            rewrite_expression = rewrite_expression.replace( dependency, dependency_name)
            # Replace only if not quoted at start
            rewrite_expression = rewrite_expression.replace( '"'+dependency_name, "__keep__")
            rewrite_expression = rewrite_expression.replace( dependency_name, '%s["%s"]["%s"]' % ( '_series', graph.graphid, dependency_name))
            rewrite_expression = rewrite_expression.replace( "__keep__", '"'+dependency_name)

        #kklog_info( '%s = %s\n' % ( _graph.graphid, rewrite_expression))
        return ( entity_assign, rewrite_expression)

    def _delete_terminal_columns( self, _series) :
        for serieid in _series :
            serie = _series.get( serieid, None)
            if serie is None :
                continue
            terminal_columns = [ terminal_column for terminal_column in serie.columns \
                if terminal_column.startswith( self._figure.datasourceseparator) ]
            if len( terminal_columns) > 0 :
                kklog_debug( 'dropping %d unused columns from %s data pool' % ( len( terminal_columns), serieid))
                serie.drop( terminal_columns, inplace=True, axis=1)

        return _series

    def _write_data( self, _series) :
        for serieid in _series :
            serie = _series.get( serieid, None)
            if serie is None or serie.empty :
                continue
            delim = self._conf.tmpdata_column_delim
            serie = serie.dropna( how='all')
            serie = serie.reset_index()
            self.create_output_directory()
            serie.to_csv( self.datapool_filename( serieid, _abs=True), header=True, \
                na_rep='na', sep=delim, index=True, index_label=['row'], date_format='%Y-%m-%dT%H:%M:%S')

