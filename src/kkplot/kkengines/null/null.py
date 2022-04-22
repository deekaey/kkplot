
## example call
## python kkplot.py -E null

from kkengines.base import kkplot_engine as kkplot_engine

from kkutils.log import *

import sys
import time

class kkplot_engine_null( kkplot_engine) :
    def  __init__( self, _conf=None) :
        super( kkplot_engine_null, self).__init__( "null", _conf, None)

    def  new( self, _conf, _dviplot) :
        engine_null = kkplot_engine_null( _conf)
        return  engine_null

    def  __str__( self) :
        return  self.name;

    def  help( self) :
        return "no help"

    def  generate( self) :
        return 0

    def  write( self, _target=None) :
        pass
    @property
    def  suffix( self) :
        return ''

__kkplot_engine_null_factory = kkplot_engine_null()

