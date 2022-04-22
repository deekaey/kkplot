
from kkplot.kkutils.log import *
import os
import argparse

class kkplot_configuration( object) :

    def  __init__( self, _engines) :

        self.basedirvars = dict( table='KKPLOT_TABLESDIR', outputs='KKPLOT_OUTPUTSDIR', tmp='KKPLOT_TMPDIR',
            measurements='KKPLOT_MEASUREMENTSDIR', providers='KKPLOT_PROVIDERSDIR')

        parser = argparse.ArgumentParser()

        parser.add_argument( '-E','--engine', default=None,
            help='plot engine {%s}' % ', '.join(_engines))
        parser.add_argument( '-o','--engine-options', default='',
            help='ampersand (&) separated list of engine options')
        parser.add_argument( '-j','--engine-help', action='store_true',default=False,
            help='print engine specific help')
        parser.add_argument( '--list-engines', action='store_true',default=False,
            help='list available engines')

        parser.add_argument( '--bundle', action='store_true',default=False,
            help='create directory containing everything needed to produce figure.')
        parser.add_argument( '--output', default=None,
            help='file name for resulting figure (by default the value of the \'output\' attribute in the figure description is used, \"kkplot.png\" if attribute is not set)')
        parser.add_argument( '--outputformat', default=None,
            help='file format for resulting figure (by default the value of the \'outputformat\' attribute in the figure description is used, \"png\" if attribute is not set)')

        parser.add_argument( '--outputs-dir', default=None,
            help='directory where output files are written (default=".", overwrites environment variable `KKPLOT_OUTPUTSDIR\')')
        parser.add_argument( '--tmp-dir', default=None,
            help='directory where output temporary files are written (default=".", overwrites environment variable `KKPLOT_TMPDIR\')')

        parser.add_argument( '--data-dir', default=None,
            help='base directory for data sources (e.g., model outputs), (default=".", overwrites environment variable `KKPLOT_DATADIR\')')
        parser.add_argument( '--measurements-dir', default=None,
            help='base directory for measurement data (e.g., observations of nitrate leaching rates), (default=".", overwrites environment variable `KKPLOT_MEASUREMENTSDIR\')')
        parser.add_argument( '--providers-dir', default=None,
            help='base directory for data providers (e.g., measurements parser), (default=".", overwrites environment variable `KKPLOT_PROVIDERSDIR\')')

        parser.add_argument( '-D','--env', action='append', default=None,
            help='define additional environment variables, can be given multiple times (e.g., -DPROJECTS_DIR=/home/projects)')

        parser.add_argument( '-d','--tmpdata-column-delim', default=',',
            help='temporary data file column delimiter (default=",")')

        parser.add_argument( '-z','--no-run-engine', action='store_true', default=False,
            help='prepare data for plotting without rerunning plot engine')

        parser.add_argument( '-Z','--no-update-data', action='store_true', default=False,
            help='run engine without updating data, assuming that these already exist in the cache (use carefully! this might not work in all situations)')

        parser.add_argument( '--debug', action='store_true', default=False,
            help='switch on debug mode')


        parser.add_argument( '-V', '--version', action='store_true', default=False,
            help='show version')


        parser.add_argument( 'plotfile', nargs='?', default='-',
            help='YAML figure description file (default="-" (stdin))')

        parser.add_argument( '--components', default=None,
            help='Only figure components are plotted, e.g., no html is created for bokeh engine')

        self.args = parser.parse_args()

        kklog.set_debug( self.args.debug)
        kklog.set_color( self.args.debug)

        self.set_environment()
        self.set_basedirs()
        self.set_engineoptions()

    @property
    def  showversion( self) :
        return  self.args.version

    @property
    def  engine( self) :
        return  self.args.engine
    def  engine_help( self) :
        return  self.args.engine_help
    def  list_engines( self) :
        return  self.args.list_engines

    def  plotfile( self) :
        return  self.args.plotfile

    @property
    def  bundle( self) :
        return  self.args.bundle
    @property
    def  output( self) :
        return  self.args.output
    @property
    def  outputformat( self) :
        return  self.args.outputformat

    def  outputs_dir( self) :
        return  self.base_dir_for( 'outputs')
    def  tmp_dir( self) :
        return  self.base_dir_for( 'tmp')
    def  data_dir( self) :
        return  self.base_dir_for( 'table')
    def  measurements_dir( self) :
        return  self.base_dir_for( 'measurements')
    def  providers_dir( self) :
        return  self.base_dir_for( 'providers')
    def  base_dir_for( self, _kind) :
        if _kind in self.basedirvars :
            return os.environ.get( self.basedirvars[_kind])
        else :
            raise RuntimeError( 'unknown data kind  [%s]' % ( _kind))

    def  option( self, _key, _delim=None) :
        if _key in self.gopts.keys() :
            gopt = self.gopts[_key].strip()
            if _delim and _delim in gopt :
                return  gopt.split( _delim)
            if _delim :
                return [ gopt]
            return  gopt
        return  ''

    @property
    def  components( self) :
        return  self.args.components

    @property
    def  tmpdata_column_delim( self) :
        return  self.args.tmpdata_column_delim
    @property
    def  skip_data_collection( self) :
        return  self.args.no_update_data
    @property
    def  skip_engine( self) :
        return  self.args.no_run_engine


    def  __str__( self) :
        return  'options:%s' % ( self.gopts)

    
    def set_basedirs( self) :
        ## "table"
        tablesdir = self.args.data_dir
        if tablesdir is None :
            tablesdir = os.environ.get( 'KKPLOT_DATADIR')
        if tablesdir is None :
            tablesdir = os.environ.get( 'KKPLOT_TABLESDIR')
        if tablesdir is None :
            tablesdir = os.environ.get( 'PLOTTER_SOURCE_PATH')
        if tablesdir is None :
            tablesdir = '.'
        tablesdir = self.normalize_dir( tablesdir)
        os.environ['KKPLOT_DATADIR'] = tablesdir
        os.environ['KKPLOT_TABLESDIR'] = tablesdir

        ## "measurements"
        measurementsdir = self.args.measurements_dir
        if measurementsdir is None :
            measurementsdir = os.environ.get( 'KKPLOT_MEASUREMENTSDIR')
        if measurementsdir is None :
            measurementsdir = os.environ.get( 'PLOTTER_MEASUREMENTS_PATH')
        if measurementsdir is None :
            measurementsdir = '.'
        measurementsdir = self.normalize_dir( measurementsdir)
        os.environ['KKPLOT_MEASUREMENTSDIR'] = measurementsdir

        ## "providers"
        providersdir = self.args.providers_dir
        if providersdir is None :
            providersdir = os.environ.get( 'KKPLOT_PROVIDERSDIR')
        if providersdir is None :
            providersdir = os.environ.get( 'PLOTTER_HOME')
        if providersdir is None :
            providersdir = '.'
        providersdir = self.normalize_dir( providersdir)
        os.environ['KKPLOT_PROVIDERSDIR'] = providersdir

        ## "outputs"
        outputsdir = self.args.outputs_dir
        if outputsdir is None :
            outputsdir = os.environ.get( 'KKPLOT_OUTPUTSDIR')
        if outputsdir is None :
            outputsdir = '.'
        outputsdir = self.normalize_dir( outputsdir)
        os.environ['KKPLOT_OUTPUTSDIR'] = outputsdir

        ## "tmp"
        tmpdir = self.args.tmp_dir
        if tmpdir is None :
            tmpdir = os.environ.get( 'KKPLOT_TMPDIR')
        if tmpdir is None :
            tmpdir = '.'
        tmpdir = self.normalize_dir( tmpdir)
        os.environ['KKPLOT_TMPDIR'] = tmpdir

    def normalize_dir( self, _basedir) :
        return _basedir.replace( '\\', '/').strip()

    def set_environment( self) :
        if self.args.env is None :
            return
        for envvar in self.args.env :
            value = ''
            name_and_value = envvar.split( '=', 1)
            if len( name_and_value) == 1 : ## 'name'
                pass
            else : ## 'name=value'
                value = name_and_value[1].strip()
            name = name_and_value[0].strip()
            if name == '' :
                kklog_fatal( 'empty environment variable name')
            os.environ[name] = value

    def set_engineoptions( self) :
        gopts_l = self.args.engine_options.split( '&')
        self.gopts = dict()
        for opt in gopts_l :
            key, value = ( opt, 'on')
            if '=' in opt :
                key, value = opt.split( '=', 1)
            key = key.strip()
            if key != '' :
                self.gopts[key] = value

