
from .writer import kkplot_writer as writer
from .conf import kkplot_configuration as configuration
#from expand import kkplot_expand as kkexpand
from .log import *

import sys
def programname( _path=None) :
    b = _path
    if b is None :
        b = sys.argv[0]
    b = b.split( '/')
    b = b[-1]
    b = b.split( '\\')
    b = b[-1]
    b = b[0:3].upper()+b[3:-3]
    return b


def auto_layout( _n_tiles, _min_rows=1, _min_cols=1) :
    if _n_tiles == 1 : ## hack?!
        return 1, 1
## TODO drop inapplicable configurations (i.e., use _min_rows and _min_cols)
    penalty_min = 10000.0
    M, N = ( _n_tiles, 1)
    for n in range( 1, _n_tiles+1) :
        for m in range( 1+int( _n_tiles/n), 1, -1) :
            if m*n < _n_tiles :
                continue

            penalty = abs( _n_tiles - ( m*n)) + abs( 0.5*( m-n))
            if penalty < penalty_min :
                penalty_min = penalty
                M, N = m, n
    return M, N

def pack( _R, _C, _extents, _strategies=None, _alignment=None) :
    strategies = _strategies
    if strategies is None :
        strategies = [ 'greedybestfit' ]
    elif isinstance( strategies, str ) :
        strategies = [ strategies ]
    result = None
    lt = lambda x,y: x<y
    gt = lambda x,y: x>y
    for strategy, rel in zip( [ s for s in strategies for _ in range( 2 ) ], ( gt, lt )*len( strategies ) ):
        if strategy == 'greedybestfit' :
            result = pack_greedybestfit( _R, _C, _extents, rel)
        elif strategy == 'static' :
            _R, _C, result = pack_static( _R, _C, _extents, rel, _alignment)            
        else:
            kklog_fatal( 'unknown pack strategy "%s"' % ( strategy ) )
        if result :
            break
    return _R, _C, result

def pack_greedybestfit( _M, _N, _extents, _cmp) :
    result = dict()
    W = [ ( _M, _N, 0, 0 ) ]
    w_k = None
    for j, m, n in _extents :
        k = -1
        for i, w in enumerate( W ) :
            if w[0] >= m and w[1] >= n :
                if k == -1 or w_k[0]*w_k[1] > w[0]*w[1] :
                    k = i
                    w_k = w
        if k == -1 :
            ## unable to satisfy request
            return None
        else:
            M, N = w_k[0], w_k[1]
            if _cmp( M*(N-n), N*(M-m) ) :
                w_split = [ ( M, N-n, 0, n ), ( M-m, n, m, 0 ) ]
            else :
                w_split = [ ( M-m, N, m, 0 ), ( m, N-n, 0, n ) ]
            W_dup = list( W )
            W = list()
            for i, w in enumerate( W_dup ) :
                if i == k :
                    for w1, w2, w3, w4 in w_split :
                        if w1 > 0 and w2 > 0 :
                            W.append( ( w1, w2, w3+w_k[2], w4+w_k[3] ) )
                else :
                    W.append( w )
        result[j] = ( m, n, w_k[2], w_k[3] )
    return result


def pack_static( _R, _C, _extents, _cmp, _alignment=None) :
    pxy = [[(r,c) for c in range(_C)] for r in range(_R)]
    result = dict()
    W = [ ( _R, _C, 0, 0 ) ]
    
    rowsfirst = True
    if _alignment :
        if 'columnsfirst' in _alignment :
            rowsfirst = False
    for j, m, n in _extents :
        span = (m, n)
        px = py = -1
        pxi = pyi = 0
        while True :
            slot_okay = True

            px = pxy[pyi][pxi][1]
            py = pxy[pyi][pxi][0]

            #check if slot unused
            if (px < 0) or (py < 0) :
                slot_okay = False
            
            #check if neighbour slots are unused
            if slot_okay :
                for cx in range(pxi, pxi+span[1]) :
                    for cy in range(pyi, pyi+span[0]) :
                        #check if we are inside boundaries
                        if (cx < len(pxy[0])) and (cy < len(pxy)):
                            if (pxy[cy][cx][0] < 0.0) or (pxy[cy][cx][1] < 0.0) :
                                #neighbour slot already used
                                slot_okay = False
                                break
                        else :
                            #outside boundaries
                            slot_okay = False
                            break
            #iterate to next slot
            if not slot_okay :
                if rowsfirst :
                    pxi += 1
                    if pxi == _C :
                        pxi = 0
                        pyi += 1
                else :
                    pyi += 1
                    if pyi == _R :
                        pyi = 0
                        pxi += 1

                if (pxi == _C) or (pyi == _R) :
                    pxy.append(  [(_R,c) for c in range(_C)] )
                    pxi = 0
                    pyi = 0
                    _R += 1
                    #return -1
                elif (pxi == _C) or (pyi == _R) :
                    kklog_error( 'invalid graph ID')
                    return -1
            else :
                break
        #mark slot as used
        for cx in range( pxi, pxi+span[1]) :
            for cy in range( pyi, pyi+span[0]) :
                pxy[cy][cx] = (-1,-1)
        
        result[j] = ( m, n, py, px )
    return _R, _C, result
