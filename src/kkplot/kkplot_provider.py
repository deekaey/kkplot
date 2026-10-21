
from kkplot.kkutils.log import *
from kkplot.kkutils.expand import *
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
        if self._program is None :
            return 0
        if self._program == 'python' and len( self._args) > 0 and self._args[0].endswith( '.py') :
            return self._execute_python_inprocess( self._args[0], self._args[1:])
        import subprocess
        return subprocess.call( [ self._program] + self._args)

    ## run python providers inside this interpreter: saves starting
    ## a new python (and importing pandas) for every data source
    def _execute_python_inprocess( self, _script, _args) :
        import runpy
        import sys
        import traceback
        saved_argv, saved_path = sys.argv, list( sys.path)
        sys.argv = [ _script] + list( _args)
        sys.path.insert( 0, os.path.dirname( os.path.abspath( _script)))
        try :
            runpy.run_path( _script, run_name='__main__')
            rc = 0
        except SystemExit as exit :
            rc = exit.code if isinstance( exit.code, int) else ( 0 if exit.code is None else 1)
        except Exception :
            traceback.print_exc()
            rc = 1
        finally :
            sys.argv, sys.path[:] = saved_argv, saved_path
            sys.stdout.flush()
        return rc

    def __str__( self) :
        return  '%s %s' % ( self._program, ' '.join( [ '"%s"' % ( arg) for arg in self._args]))

