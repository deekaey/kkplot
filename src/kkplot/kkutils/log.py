
import sys

class kkplot_log( object) :

    def  __init__( self) :
        self._stream = sys.stderr
        self._debug = False
        self._color = False

    def log_write( self, _prefix, _colorprefix, _msg='  ') :
        if self._color :
            self._stream.write( '[%s] %s\n' % ( _colorprefix, str( _msg)))
        else :
            self._stream.write( '[%s] %s\n' % ( _prefix, str( _msg)))

    def log_verbose( self, _msg) :
        self.log_write( 'II', '\033[00;32;1mII\033[00m', _msg)
    def log_info( self, _msg) :
        self.log_write( 'II', '\033[00;32;1mII\033[00m', _msg)
    def log_warn( self, _msg) :
        self.log_write( 'WW', '\033[00;33;1mWW\033[00m', _msg)
    def log_error( self, _msg) :
        self.log_write( 'EE', '\033[00;31;1mEE\033[00m', _msg)
    def log_fatal( self, _msg) :
        self.log_write( 'FF', '\033[00;31;1mFF\033[00m', _msg)
        sys.exit( 255)
    def log_debug( self, _msg) :
        if self._debug :
            self.log_write( 'DD', '\033[00;30;1mDD\033[00m', _msg)

    def set_debug( self, _yesno) :
        self._debug = _yesno
    def set_color( self, _yesno) :
        self._color = _yesno

kklog = kkplot_log()

def  kklog_verbose( _msg) :
    kklog.log_verbose( _msg)
def  kklog_info( _msg) :
    kklog.log_info( _msg)
def  kklog_warn( _msg) :
    kklog.log_warn( _msg)
def  kklog_error( _msg) :
    kklog.log_error( _msg)
def  kklog_fatal( _msg) :
    kklog.log_fatal( _msg)
def  kklog_debug( _msg) :
    kklog.log_debug( _msg)

