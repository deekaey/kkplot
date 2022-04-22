
from kkutils.log import *
from kkutils.expand import *
import os

class kkplot_provider( object) :
    def __init__( self, _program=None, _args=[], _program_basedir='.') :
        self._program = _program
        self._args = _args
        if self._args is None :
            self._args = []

        if self._program is None :
            pass
        elif type( self._program) is str :
            self._program = self._program.strip()
        elif type( self._program) is list :
            program = self._program.pop( 0)
            self._args += self._program
            self._program = program.strip()
        else :
            raise RuntimeError( 'program must be string or list of strings')

        ## expand environment variables in arguments
        for j, arg in enumerate( self._args) :
            self._args[j] = kkexpand( arg)

        ## some heuristic, check if we need an interpreter
        if self._program is not None :
            self._program = self._program.replace( '\\', '/')
            program = self._program.split( '.')
            if len( self._program) == 0 :
                self._program = None
            elif len( program) == 1 :
                ## no suffix, assume native binary
                pass
            else :
                ## investigate suffix
                program_suffix = program[-1].lower()
                INTERPRETERS =     { 'awk':'awk', 'bat':'cmd', 'm':'octave', 'pl':'perl', 'py':'python', 'r':'Rscript', 'sh':'bash', 'zsh':'zsh'}
                INTERPRETERS_OPT = { 'awk':'-f',  'bat':None,  'm':None,     'pl':None,   'py':None,     'r':None,      'sh':None, 'zsh':None}
                if program_suffix in INTERPRETERS :
                    interpreter_opt = []
                    if INTERPRETERS_OPT[program_suffix] is not None :
                        interpreter_opt = [ INTERPRETERS_OPT[program_suffix]]
                    if not os.path.isabs( self._program) :
                        self._program = _program_basedir + '/' + self._program
                    self._args = interpreter_opt + [ self._program ] + self._args
                    self._program = INTERPRETERS[program_suffix]
                else :
                    ## again, assume native binary (e.g., program.exe)
                    pass


    def execute( self) :
        if self._program is not None :
            import subprocess
            rc = subprocess.call( [ self._program] + self._args)
            return rc
        return 0

    def __str__( self) :
        return  '%s %s' % ( self._program, ' '.join( [ '"%s"' % ( arg) for arg in self._args]))

