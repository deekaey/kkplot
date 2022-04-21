
from kkutils.log import *
import os

def  kkexpand( _string) :
    estr = _string
    if estr is not None :
        estr = os.path.expandvars( estr)
    return  estr

