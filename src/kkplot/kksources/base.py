
from kkutils.log import *

import datetime as datetime
import pandas as pandas
import numpy as numpy

class kkplot_domainparser( object) :
    def __init__( self, _args=dict()) :
        self._args = _args

    def arg( self, _arg, _default=None) :
        return self._args.get( _arg, _default)

    def construct_domaincolumns( self, _entity_data, _domain) :
        return _entity_data

class kkplot_timeparser( kkplot_domainparser) :
    def __init__( self, _args) :
        super( kkplot_timeparser, self).__init__( _args)

class kkplot_spaceparser( kkplot_domainparser) :
    def __init__( self, _args) :
        super( kkplot_spaceparser, self).__init__( _args)

class kkplot_noneparser( kkplot_domainparser) :
    def __init__( self, _args) :
        super( kkplot_noneparser, self).__init__( _args)


import time
import calendar
class kkplot_timeparser_ldndcyj( kkplot_timeparser) :
    def __init__( self, _args) :
        super( kkplot_timeparser_ldndcyj, self).__init__( _args)

        self.juliandaymonth = \
            [ 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12]
        self.juliandaymonthleapyear = \
            [ 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12]

        self.juliandayday = \
            [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
        self.juliandaydayleapyear = \
            [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]

        self.M = { True:self.juliandaymonthleapyear, False:self.juliandaymonth }
        self.D = { True:self.juliandaydayleapyear, False:self.juliandayday }

    def isleapyear( self, _year) :
        return calendar.isleap( _year)
    def julianday_to_datetime( self, _year, _julianday) :
        month = self.M[self.isleapyear( _year)][int(_julianday)]
        day = self.D[self.isleapyear( _year)][int(_julianday)]
        return datetime.datetime( _year, month, day)

    @property
    def source_domaincolumns( self) :
        return [ 'year', 'julianday'] ## TODO [ 'subday']
        
    ## TODO subday (auto-detect)
    def construct_domaincolumns( self, _entity_data, _domain) :
        if _domain.domaincolumns[0] in _entity_data.columns :
            return _entity_data

        data_columns = _entity_data.columns
        if 'year' in data_columns and 'julianday' in data_columns :
            date_parser_ser = lambda Y, J : pandas.Series( [ self.julianday_to_datetime( y, j) for ( y,j) in zip( Y,J)])
            _entity_data[_domain.domaincolumns[0]] = date_parser_ser( _entity_data['year'], _entity_data['julianday'])
        else :
            raise RuntimeError( 'LdndcYJ: temporal data file lacks domain columns  [expect columns %s]' \
                % ( ", ".join( [ '"%s"' % column for column in self.source_domaincolumns])))
        return _entity_data



class kkplot_timeparser_ldndcy( kkplot_timeparser) :
    def __init__( self, _args) :
        super( kkplot_timeparser_ldndcy, self).__init__( _args)

    @property
    def source_domaincolumns( self) :
        return [ 'year']

    def year_to_datetime( self, _year) :
        month = 12
        day = 31
        return datetime.datetime( _year, month, day)


    def construct_domaincolumns( self, _entity_data, _domain) :
        if _domain.domaincolumns[0] in _entity_data.columns :
            return _entity_data

        data_columns = _entity_data.columns
        if 'year' in data_columns :
            date_parser_ser = lambda Y : pandas.Series( [ self.year_to_datetime( y) for y in Y])
            _entity_data[_domain.domaincolumns[0]] = date_parser_ser( _entity_data['year'])
        else :
            raise RuntimeError( 'LdndcY: temporal data file lacks domain columns  [expect columns %s]' \
                               % ( ", ".join( [ '"%s"' % column for column in self.source_domaincolumns])))
        return _entity_data

import dateutil.parser
class kkplot_timeparser_iso8601( kkplot_timeparser) :
    def __init__( self, _args) :
        super( kkplot_timeparser_iso8601, self).__init__( _args)

    @property
    def source_domaincolumns( self) :
        return [ 'datetime']

    def iso8601_to_datetime( self, _iso8601) :
        return dateutil.parser.parse( _iso8601)

    def construct_domaincolumns( self, _entity_data, _domain) :
        if _domain.domaincolumns[0] in _entity_data.columns :
            return _entity_data

        data_columns = _entity_data.columns
        if 'datetime' in data_columns :
            date_parser_ser = lambda Y : pandas.Series( [ self.iso8601_to_datetime( y) for y in Y])
            _entity_data[_domain.domaincolumns[0]] = date_parser_ser( _entity_data['datetime'])
        else :
            raise RuntimeError( 'ISO8601: temporal data file lacks domain columns  [expect columns %s]' \
                               % ( ", ".join( [ '"%s"' % column for column in self.source_domaincolumns])))
        return _entity_data



class kkplot_spaceparser_ldndcxyz( kkplot_spaceparser) :
    def __init__( self, _args) :
        super( kkplot_spaceparser_ldndcxyz, self).__init__( _args)
    @property
    def source_domaincolumns( self) :
        return [ 'id', 'x', 'y', 'z' ]

    def construct_domaincolumns( self, _entity_data, _domain) :
        
        if _domain.get_property( 'grid') is None :
            xylength = self.arg( 'length', 1.0)
            xlength = self.arg( 'xlength', xylength)
            ylength = self.arg( 'ylength', xlength)
            xyround = self.arg( 'xyround', 10)
            _domain.add_properties( { 'grid':True, 'xlength':xlength, 'ylength':ylength, 'xyround':xyround} )

        return _entity_data

have_shapefile = True
try :
    import shapefile
except ImportError :
    have_shapefile = False

class kkplot_spaceparser_ldndcesri( kkplot_spaceparser) :
    def __init__( self, _args) :
        super( kkplot_spaceparser_ldndcesri, self).__init__( _args)
        if not have_shapefile :
            kklog_fatal( 'No ESRI Shapefile support. We require the package Shapely')

## TODO  replace by bounding boxes
        self._centroids = None
    @property
    def source_domaincolumns( self) :
        return [ 'id' ]

    def _set_centroids( self, _ids, _domain) :
        C = _domain.domaincolumns
        d = numpy.empty(( len(_ids), len( C)))
        d.fill( 0.0)
        ixyz_dataframe = pandas.DataFrame( d, columns=C)
        ixyz_dataframe['id'] = _ids.astype( numpy.int64)
        for shapeid in self._centroids :
            pass
            #xyz_dataframe[C][_ids==shapeid] = self._centroids.shapeid
        return ixyz_dataframe


    def construct_domaincolumns( self, _entity_data, _domain) :

        if self._centroids is None or _domain.get_property( 'esriidindex') is None :
            esrishapefile = self.arg( 'esrishapefile')
            linkby = self.arg( 'linkby', 'id')

            #kklog_debug( 'esri=%s' % ( esrishapefile))
            if esrishapefile is None :
                kklog_error( 'failed to read ESRI Shapefile  [file=%s]' % ( esrishapefile))
                return None
            else :
                self._centroids = self._read_esri( esrishapefile, linkby, _domain)
            if self._centroids is None :
                return None
## sk: does this break -X ?
            _domain.add_properties( { 'esrishapefile':esrishapefile, 'esrilinkby':'id'} )

        ## NOTE assume we are done...
        if len( [ c for c in _domain.domaincolumns if c in _entity_data.columns]) == len( _domain.domaincolumns) :
            return _entity_data

        _entity_data[_domain.domaincolumns] = \
            self._set_centroids( _entity_data['id'], _domain)
        return _entity_data

    def _read_esri( self, _esrishapefile, _linkby, _domain) :
        z = self.arg( 'z', 'elevation')

        centroids = dict()
        esri = shapefile.Reader( _esrishapefile)
        id_index = self._field_at( esri, _linkby)
        if id_index == -1 :
            kklog_error( 'shape linking attribute not found  [linkby=%s]' % ( _linkby))
            return None
        _domain.add_properties( { 'esriidindex':id_index })
        z_index = self._field_at( esri, z)
        for element in esri.shapeRecords() :
            shapeid = element.record[id_index]
            #print element.record, shapeid

            centroids[shapeid] = list()
            centroid_z = 0.0 if z_index == -1 else element.record[z_index]

            points = numpy.array( element.shape.points)
            centroids[shapeid].append(( points[0][0], points[0][1], centroid_z))
        return centroids

    def _field_at( self, _esri, _linkby) :
        linkby_index = 0
        for ( name, dtype, size, deci) in _esri.fields :
            if name == 'DeletionFlag' :
                continue
            elif name == _linkby :
                return linkby_index
            else:
                linkby_index += 1
        return -1


class kkplot_noneparser_table( kkplot_noneparser) :
    def __init__( self, _args) :
        super( kkplot_noneparser_table, self).__init__( _args)

    @property
    def source_domaincolumns( self) :
        return [ ]

    def construct_domaincolumns( self, _entity_data, _domain) :
        return _entity_data


KKPLOT_DOMAINPARSERS = dict( \
    iso8601=kkplot_timeparser_iso8601, \
    ldndcyj=kkplot_timeparser_ldndcyj, \
    ldndcy=kkplot_timeparser_ldndcy, \
    ldndcxyz=kkplot_spaceparser_ldndcxyz, \
    ldndcesri=kkplot_spaceparser_ldndcesri, \
    table=kkplot_noneparser_table)

class kkplot_domainparsers( object) :
    def __init__( self, _parsers) :
        self._parsers = _parsers

    def construct_parser( self, _flavor, _flavorargs) :
        domain_parser = self._parsers.get( _flavor)
        if domain_parser :
            return domain_parser( _flavorargs)
        return None

kkplot_domainparserfactory = kkplot_domainparsers( KKPLOT_DOMAINPARSERS)


KKPLOT_SOURCES = dict()
class kkplot_source( object) :
    def  __init__( self, _format) :
        self._format = _format
        self._parser = None

        global KKPLOT_SOURCES
        if not self._format in KKPLOT_SOURCES :
            KKPLOT_SOURCES[self._format] = self

    def  construct_parser( self, _flavor, _flavorargs) :
        self._parser = kkplot_domainparserfactory.construct_parser( _flavor, _flavorargs)
        return self._parser

    def  open( self, _source) :
        sys.stderr.write( "method 'open' not implemented\n")
    def  read( self, _graph, _querycolumns, _targetcolumns, _select) :
        sys.stderr.write( "method 'read' not implemented\n")

    def  make_columns( self, _querycolumns, _targetcolumns,
            _groupcolumns, _selectcolumns, _filtercolumnslist, _datacolumns) :
        filtercolumns = dict()
        for columns in _filtercolumnslist :
            for column in columns :
                filtercolumns[column] = 1

        querycolumns = list( _querycolumns)
        targetcolumns = list( _targetcolumns)
        for j, filtercolumn in enumerate( filtercolumns.keys()) :
            if filtercolumn not in querycolumns :
                if filtercolumn in _datacolumns :
                    querycolumns.append( filtercolumn)
                    targetcolumns.append( filtercolumn)

        groupcolumns = list()
        selectcolumns = list()
        for groupcolumn, selectcolumn in zip( _groupcolumns, _selectcolumns) :
            if groupcolumn in _datacolumns :
                groupcolumns.append( groupcolumn)
                selectcolumns.append( selectcolumn)
            else :
                if groupcolumn in [ 'year', 'month', 'day' ] :
                    selectcolumns.append( selectcolumn)
                else :
                    kklog_warn( 'dropping groupby column key  [key=%s]' % ( groupcolumn))

        return querycolumns, targetcolumns, groupcolumns, selectcolumns

    def  construct_domaincolumns( self, _querydata, _domain) :
        return self._parser.construct_domaincolumns( _querydata, _domain)

    def  filter_data( self, _querydata, _graph, _select=None) :
        ## let the domain parser do the work
        querydata = _graph.domain.filter_data( _querydata, self._parser)
        if _select :
            for k, crit in enumerate( _select) :
                groupby_key = _graph.groupname(k)
                if groupby_key not in querydata.columns :
                    if groupby_key == 'year' :
                        years = pandas.DatetimeIndex( querydata['time']).year
                        querydata = querydata[years==crit]
                    elif groupby_key == 'month' :
                        month = pandas.DatetimeIndex( querydata['time']).month
                        querydata = querydata[month==crit]
                    elif groupby_key == 'day' :
                        days = pandas.DatetimeIndex( querydata['time']).day
                        querydata = querydata[days==crit]
                    else :
                        kklog_error( 'missing column  [column=%s]' % ( groupby_key))
                        return None
                else :
                    querydata = querydata[querydata[groupby_key]==crit]
        return querydata

    @property
    def  name( self) :
        return self._format
    @property
    def  source_domaincolumns( self) :
        return self._parser.source_domaincolumns

def  create( _datasource) :
    if _datasource.format in KKPLOT_SOURCES :
        rdr = KKPLOT_SOURCES[_datasource.format].new()
        rdr.construct_parser( _datasource.flavor, _datasource.flavorargs)
        return  rdr
    return  None

def  names() :
    return  KKPLOT_SOURCES.keys()

