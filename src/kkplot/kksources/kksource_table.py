
from kkplot.kkutils.log import *
from kkplot.kksources.base import kkplot_source as kkplot_source

import pandas as pandas

class kkplot_source_table( kkplot_source) :
    def  __init__( self, _name='table') :
        super( kkplot_source_table, self).__init__( _name)
        self._data = None

    def  new( self) :
        return kkplot_source_table()

    def  __str__( self) :
        return self.name;

    def  open( self, _source) :
        if self._data is None :
            kklog_debug( 'opening data source [%s]' % ( _source))
            try :
                data = pandas.read_csv( _source, header=0, na_values=['-99.99','na','nan'], comment='#', sep="\t")
            except IOError as ioerr :
                kklog_error( 'Table reader: %s' % ( ioerr))
                return None
            data = self.canonicalize_headernames( data)
            self._data = data
        return self

    @property
    def  _data_columns( self) :
        return  self._data.columns

    def  read( self, _graph, _querycolumns, _targetcolumns, _select) :

        self._data = self.construct_domaincolumns( self._data, _graph.domain)

        querycolumns, targetcolumns, groupcolumns, selectcolumns = self.make_columns( \
            _querycolumns, _targetcolumns, _graph.groups(), _select, \
            [ _graph.groups(), _graph.domain.domaincolumns], self._data_columns )

        querydata = pandas.DataFrame()

        querydata[targetcolumns] = self._data[querycolumns]
        querydata = self.filter_data( querydata, _graph, selectcolumns)
        if querydata is None :
            return None

        ## drop no longer needed columns
        G = groupcolumns
        Q = _querycolumns + _graph.domain.domaincolumns
        querydata = querydata.drop([ c for c in G if c not in Q], axis=1)

        return querydata

    ## strip off units, e.g., "colX[kgm-2]" -> "colX"
    def canonicalize_headernames( self, _querydata) :
        data_columns = _querydata.columns
        unit_offs = lambda L, pos : L if pos == -1 else pos
        _querydata.columns = [ c[:unit_offs( len(c), c.find( '['))] for c in data_columns ]
        return _querydata

__kkplot_source_table_factory = kkplot_source_table()


## alias
class kkplot_source_txt( kkplot_source_table) :
    def  __init__( self) :
        super( kkplot_source_txt, self).__init__( 'txt')

    def  new( self) :
        return kkplot_source_txt()

__kkplot_source_table_factory = kkplot_source_txt()

