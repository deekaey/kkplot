
from kkplot.kkutils.log import *

import datetime
import dateutil.parser

DOMAIN_NON = 'non'
DOMAINCOLUMNS_NONE = [ ]
DOMAIN_SPACE = 'space'
DOMAINCOLUMNS_SPACE = [ 'id', 'x', 'y', 'z' ]
DOMAIN_TIME = 'time'
DOMAINCOLUMNS_TIME = [ 'time' ]


class kkplot_domain( object) :
    def __init__( self) :
        self._properties = dict()

    def add_properties( self, _properties) :
        self._properties.update( _properties)
    def get_property( self, _propertyname, _default=None) :
        return self._properties.get( _propertyname, _default)


class kkplot_domain_time( kkplot_domain) :
    def __init__( self, _time=None) : ## format: 'YYYY-MM-DD->YYYY-MM-DD'
        super( kkplot_domain_time, self).__init__()
        self._set_time( _time)

    @property
    def kind( self) :
        return DOMAIN_TIME
    @property
    def domaincolumns( self) :
        return DOMAINCOLUMNS_TIME

    def _set_time( self, _time) :
        if _time is None :
            return self._set_time( '1970-01-01->2100-01-01')
        ## TODO needs tweaking for subday support
        if _time.find( '->') == -1 :
            t_from = _time
            t_to = t_from
        else :
            t_from, t_to = _time.split( '->')

        self._from = dateutil.parser.parse( t_from)
        self._to = dateutil.parser.parse( t_to)

        if ( self._to - self._from ) < datetime.timedelta( 0) :
            raise RuntimeError( 'illegal time specification; \'to\' before \'from\' [time=%s]' % ( self))

    @property
    def t_from( self) :
        return  self._from
    @property
    def t_to( self) :
        return  self._to

    def time_delta( self, _timeresolution="day") :
        time_delta = self.t_to - self.t_from
        if _timeresolution == "second" :
            time_delta_res = ( time_delta.days * 86400.0) + time_delta.seconds
        elif _timeresolution == "minute" :
            time_delta_res = ( time_delta.days * 1440.0) + time_delta.seconds/60.0
        elif _timeresolution == "hour" :
            time_delta_res = ( time_delta.days * 24) + time_delta.seconds/3600.0
        elif _timeresolution == "year" :
            time_delta_res = ( time_delta.days / 365.25)
        else :
            ## every other string interpreted as days
            time_delta_res = time_delta.days
        return  float( time_delta_res)

    def time_period( self, _timeresolution) :
        return self.time_delta( _timeresolution)

    def filter_data( self, _querydata, _domainparser) :
        querydata = _domainparser.construct_domaincolumns( _querydata, self)
        if querydata is None :
            return None

        tC, = self.domaincolumns
        d = querydata
        d = d[(d[tC]>=self.t_from)&(d[tC]<=self.t_to)]
        return d

    def __str__( self) :
        return '%s->%s' % ( str(self._from), str(self._to))


class kkplot_domain_space( kkplot_domain) :
    def __init__( self, _space=None) : ## format: x0:x1[,y0:y1[,z0:z1]]
        super( kkplot_domain_space, self).__init__()
        self._space = self._set_space( _space)

    @property
    def kind( self) :
        return DOMAIN_SPACE
    @property
    def domaincolumns( self) :
        return DOMAINCOLUMNS_SPACE


    def _set_space( self, _space) :
        if _space is None or len( _space) == 0 :
            return self._set_space( ':,:,:')

        xyz = [ s.strip() for s in _space.split( ',')]
        if len( xyz) > 0 :
            x0, x1 = self._get_limits( xyz[0])
        else :
            x0, x1 = self._get_limits( '')
        if len( xyz) > 1 :
            y0, y1 = self._get_limits( xyz[1])
        else :
            y0, y1 = self._get_limits( '')
        if len( xyz) > 2 :
            z0, z1 = self._get_limits( xyz[2])
        else :
            z0, z1 = self._get_limits( '')
        return [ x0, x1, y0, y1, z0, z1]

    def _get_limits( self, _limits) :
        if len( _limits) == 0 or _limits == ':' :
            return self._get_limits( '-inf:inf')
        limits = _limits.split( ':')
        if len( limits) == 1 :
            return ( float( limits[0]), float( 'inf'))
        if len( limits) == 2 :
            if len( limits[0]) == 0 :
                limits[0] = -float( 'inf')
            else :
                limits[0] = float( limits[0])
            if len( limits[1]) == 0 :
                limits[1] = float( 'inf')
            else :
                limits[1] = float( limits[1])
        return ( limits[0], limits[1])

    @property
    def x0( self) :
        return self._space[0]
    @property
    def x1( self) :
        return self._space[1]
    @property
    def y0( self) :
        return self._space[2]
    @property
    def y1( self) :
        return self._space[3]
    @property
    def z0( self) :
        return self._space[4]
    @property
    def z1( self) :
        return self._space[5]

    def filter_data( self, _querydata, _domainparser) :
        querydata = _domainparser.construct_domaincolumns( _querydata, self)
        if querydata is None :
            return None

        idC, xC, yC, zC = self.domaincolumns
        d = _querydata
        d = d[(d[xC]>=self.x0)&(self.x1>=d[xC])&(d[yC]>=self.y0)&(self.y1>=d[yC])&(d[zC]>=self.z0)&(self.z1>=d[zC])]
        return d

    def __str__( self) :
        return  '%.3f:%.3f,%.3f:%.3f,%.3f:%.3f' % \
            ( self.x0, self.x1, self.y0, self.y1, self.z0, self.z1)

class kkplot_domain_none( kkplot_domain) :
    def __init__( self, _domain=None) :
        super( kkplot_domain_none, self).__init__()

    @property
    def kind( self) :
        return 'non'
    @property
    def domaincolumns( self) :
        return DOMAINCOLUMNS_NONE

    def filter_data( self, _querydata, _domainparser) :
        return _querydata

