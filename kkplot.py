#!/usr/bin/python

import sys
import kkutils as utils
import kkengines as engines
from kkplot_dviplot import kkplot_dviplot as dviplot

from kkplot_version import __version__

def kkplot_print_enginehelp( _engine, _config=None) :
    engine = None
    if _engine is not None :
        engine = _engine
    elif _config is not None :
        engine_name = _config.engine
        if engine_name is None :
            engine_name = 'null'
        engine = engines.create( engine_name, _config, None)
    else :
        sys.stderr.write( 'no engine, no configuration, no nothing :(\n')
        return -1
    
    sys.stderr.write( 'engine options [%s]:\n%s\n' \
            % ( engine, engine.help()))
    return 0

def kkplot_list_engines() :
    sys.stdout.write( '%s\n' % ( '\n'.join( engines.names())))
    return 0

if __name__ == '__main__':

    try :
        kkplot_config = utils.configuration( engines.names())
    except :
        sys.exit( 65)

    if kkplot_config.showversion :
        sys.stdout.write( '%s %s\n' % ( utils.programname(), str(__version__)))
        sys.exit( 0)

    if kkplot_config.engine_help() :
        sys.exit( kkplot_print_enginehelp( None, kkplot_config))
    if kkplot_config.list_engines() :
        sys.exit( kkplot_list_engines())

    try :
        kkplot_plot = dviplot( kkplot_config, kkplot_config.plotfile(), 'yaml')
    except RuntimeError as err :
        utils.log.kklog_error( 'failed to assemble plot\nerror: %s\n' % ( err))
        sys.exit( 101)

    if not kkplot_config.skip_engine :
        kkengine = kkplot_config.engine
        if kkengine is None :
            kkengine = 'null' if kkplot_plot.engine is None else kkplot_plot.engine
    
        kkplot_engine = engines.create( kkengine, kkplot_config, kkplot_plot)
        if kkplot_engine is None :
            utils.log.kklog_error( 'failed to create engine [%s]\n' % ( kkengine))
            sys.exit( 102)
        elif kkplot_config.engine_help() :
            kkplot_print_enginehelp( kkplot_engine)
        else :
            rc = kkplot_engine.generate()
            if rc == 0 :
                if kkplot_config.bundle :
                    source_filename = kkplot_plot.source_filename( kkplot_engine.suffix)
                    kkplot_engine.write( source_filename)
                kkplot_engine.write()
            else :
                utils.log.kklog_error( 'failed to generate plot\n')
                sys.exit( 103)
    else :
        utils.log.kklog_debug( 'reread data, but not running engine.')

    sys.exit( 0)

