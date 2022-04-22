
from kkutils.log import *
from kksources.base import kkplot_source as kkplot_source

import pandas as pandas
import pandas.io.sql as pandas_io_sqlite3
have_sqlalchemy = True
try :
    from sqlalchemy import create_engine as sql_create_engine
except ImportError as ierr :
    have_sqlalchemy = False
    #kklog_warn( 'No sqlite support available')

class kkplot_source_sqlite3( kkplot_source) :
    def  __init__( self) :
        super( kkplot_source_sqlite3, self).__init__( 'sqlite3')
        self._dbengine = None
        self._args = dict()

    def  new( self) :
        return  kkplot_source_sqlite3()

    def  __str__( self) :
        return  self.name;

    def  open( self, _source) :
        if not have_sqlalchemy :
            kklog_fatal( 'No SQLite3 support. We require the package SQLAlchemy')

        source, self._args = self._extract_arguments( _source)
        kklog_debug( 'connecting to database... [%s]' % ( source))
        try :
            self._dbengine = sql_create_engine( 'sqlite:///%s' % ( source))
        except :
            kklog_error( 'failed to open database "%s"' % ( source))
            self._dbengine = None
            return None
        kklog_debug( 'connected to database [%s]' % ( source))
        return self
 
    def  _extract_arguments( self, _source) :
        args = _source.split( '&')
        source = args.pop( 0) ## drop path
        return ( source, dict([ arg.split('=') for arg in args]))

    @property
    def  _data_columns( self) :
        dbquery = 'select * from %s where rowid=1;' % ( self._args['table'])
        datacolumns = pandas.read_sql_query( dbquery, self._dbengine)
        return  list( datacolumns.columns.values)

    def  read( self, _graph, _querycolumns, _targetcolumns, _select) :
        querycolumns, targetcolumns, groupcolumns, selectcolumns = self.make_columns( \
            _querycolumns, _targetcolumns, _graph.groups(), _select, \
            [ _graph.groups(), self.source_domaincolumns], self._data_columns )

        sql_query = self._construct_sql_query( _graph, querycolumns, _select)
        kklog_debug( 'sql="%s"' % ( sql_query))
        querydata = pandas.DataFrame()
        try :
            querydata[targetcolumns] = pandas.read_sql_query( sql_query, self._dbengine)
            querydata = self.filter_data( querydata, _graph)
        except IOError as ioerr :
            kklog_error( 'SQLite3 reader: %s' % ( ioerr))
            return None

        if querydata is None :
            return None

        ## drop no longer needed columns
        G = groupcolumns + self.source_domaincolumns
        Q = _querycolumns + _graph.domain.domaincolumns
        querydata = querydata.drop([ c for c in G if c not in Q], axis=1)

        return querydata

    def  _construct_sql_query( self, _graph, _querycolumns, _select) :
        columns = ','.join( _querycolumns)
        where = ' AND '.join( [ '%s=%s' % ( _graph.groupname(k), crit) for ( k, crit) in enumerate( _select)])
        if where != '' :
            where = 'where %s' % ( where)
        table = self._args['table']
        return 'select %s from %s %s;' % ( columns, table, where)


__kkplot_source_sqlite3_factory = kkplot_source_sqlite3()

