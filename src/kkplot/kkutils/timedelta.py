
import datetime
from kkplot.kkutils.log import *
def  parse_timedelta( _timedelta) :

    units = { 'w':'weeks', 'd':'days', 'h':'hours', 'm':'minutes', 's':'seconds' }

    timedelta = _timedelta.strip()
    if timedelta == '' or timedelta == '+' or timedelta == '-' :
        return datetime.timedelta( 0)

    sgn = +1
    if timedelta[0] == '-' :
        sgn = -1
        timedelta = timedelta[1:]
    elif timedelta[0] == '+' :
        sgn = +1
        timedelta = timedelta[1:]
    else :
        pass

    timedeltas = dict()

    reg = ''
    for j, c in enumerate( timedelta) :
        if c in units :
            if reg == '' :
                reg = '1'
            reg_unit = timedeltas.get( units[c], 0)
            timedeltas[units[c]] = reg_unit + sgn*int( reg)
            reg = ''
        elif c in '0123456789' :
            reg += c ## leading zeros are ok
        elif c == ' ' and reg == '' :
            pass
        else :
            kklog_error( 'invalid timedelta  [%s at %s:%d]' % ( _timedelta, c, j))
            return  None

    if reg != '' :
        kklog_error( 'trailing garbage in timedelta  [%s (%s)]' % ( _timedelta, reg))
        return  None
    #kklog_debug( '%s -> %s' % ( _timedelta, str(timedeltas)))

    return datetime.timedelta( **timedeltas)

