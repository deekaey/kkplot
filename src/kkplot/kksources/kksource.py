
from kkutils.log import *
from kksources.base import create as kksource_create

class kkplot_sourcefactory( object) :
    def  __init__( self, _source, _conf) :
        self._source = _source
        self._conf = _conf

    def  construct( self) :
        if self._source.has_provider :
            kklog_debug( 'running provider.. [%s]' % ( self._source.provider))
            rc = self._source.provider.execute()
            if rc != 0 :
                kklog_error( 'failed to execute provider [%s]' % ( self._source.provider))
                return None

        kklog_debug( 'creating reader for format "%s"' % ( self._source.format))
        source_reader = kksource_create( self._source)
        if source_reader is None :
            kklog_error( 'failed to create reader for format "%s"' % ( self._source.format))
            return None
        return source_reader.open( self._source.path)

