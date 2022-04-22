
import sys



class kkplot_writer( object) :
    def __init__( self, _stream=None, _mode='python') :

        self._error = False
        self._modes = { 'python':{ 'commenton':'#', 'commentoff':''}, 'gnuplot':{ 'commenton':'#', 'commentoff':''}, 'html':{ 'commenton':'<!--\n', 'commentoff':'\n-->'}}

        self._mode = _mode

        self._baseindentlevels = list()
        self._current_baseindentlevel = 0

        self._current_cxt = 'main'
        self._codes = dict()
        self._codes[self.context] = list()

        self._commenton, self._commentoff = ( '', '')

    @property
    def context( self) :
        return self._current_cxt
    def set_context( self, _context='main') :
        self._current_cxt = _context
        if _context in self._codes :
            self._codes[_context] = list()
        return self.context
    def unset_context( self) :
        return self.set_context()

    @property
    def indentlevel( self) :
        return self._current_baseindentlevel
    def push_indentlevel( self, _indent_level=1) :
        self._baseindentlevels.append( self._current_baseindentlevel)
        self._current_baseindentlevel = _indent_level
        return self.indentlevel
    def pop_indentlevel( self) :
        if len( self._baseindentlevels) == 0 :
            sys.stderr.write( '[BUG] no more indentation levels to pop\n')
            sys.exit( 1)
        self._current_baseindentlevel = self._baseindentlevels.pop()
        return self.indentlevel

    @property
    def error( self) :
        return self._error
    def set_error( self) :
        self._error = True
    def clear_error( self) :
        self._error = False

    def prepend( self, _code) :
        self._codes[self.context] = \
            [ self._commenton + _code + self._commentoff ] + self._codes[self.context]
    def append( self, _code) :
        self._codes[self.context] += \
            [ self._commenton + _code + self._commentoff ]
    def iappend( self, _indent_level, _code) :
        self.append( self._indent_depth( self.indentlevel + _indent_level) + _code)
    def appendnl( self, _code) :
        self.append( _code + '\n')
    def iappendnl( self, _indent_level, _code) :
        self.iappend( _indent_level, _code + '\n')
    def line( self, _code, _indent_level=0) : ## alias
        self.iappendnl( _indent_level, _code)
    def newline( self, _count=1) :
        for c in range( _count) :
            self.appendnl( '')

    def _open_stream( self, _target) :
        stream = None
        if _target is None :
            stream = sys.stdout
        elif type( _target) is file :
            stream = _target
        elif type( _target) is str :
            stream = open( _target, 'w')
        else :
            raise RuntimeError( 'stream not understood')
        return stream
    def _close_stream( self, _target, _stream) :
        if type( _target) is str :
            _stream.close()

    def write( self, _contextorder=None, _target=None) :
        if len( self._baseindentlevels) > 0 :
            sys.stderr.write( '[BUG]  indentation level stack not empty  %s\n' % ( str(self._baseindentlevels)))
            sys.exit( 1)

        stream = self._open_stream( _target)
        if self._error :
            stream.write( self._error_program())
        else :
            cxtorder = self._codes.keys() if _contextorder is None else _contextorder
            for cxt in cxtorder :
                for code in self._codes[cxt] :
                    stream.write( code)

        self._close_stream( _target, stream)

    def comment_on( self) :
        self._commenton, self._commentoff = self._get_comment()
    def comment_off( self) :
        self._commenton, self._commentoff = '', ''

    def _indent_depth( self, _indent_level) :
        if self._mode == 'python' :
            return '    ' * _indent_level
        elif self._mode == 'gnuplot' :
            return '  ' * _indent_level
        elif self._mode == 'html' :
            return '  ' * _indent_level
        else :
            return '\t' * _indent_level

    def _get_comment( self) :
        if self._mode in self._modes :
            return ( self._modes[self._mode]['commenton'], self._modes[self._mode]['commentoff'])
        return '#'

    def _error_program( self) :
        if self._mode == 'python' :
            return self._error_program_python()
        elif self._mode == 'gnuplot' :
            return self._error_program_gnuplot()
        elif self._mode == 'html' :
            return self._error_program_html()
        else :
            return ''

    def _error_program_gnuplot( self) :
        return '## '
    def _error_program_python( self) :
        return 'print( "error")'
    def _error_program_html( self) :
        return '<html>error</html>'

