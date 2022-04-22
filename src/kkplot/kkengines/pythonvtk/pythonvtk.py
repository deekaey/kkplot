
## example call
## python kkplot.py -E vtk examples/kkplot-demo-vtk.yaml
##
## supported output formats:
##  vtr vtu

from kkplot.kkengines.base import kkplot_engine as kkplot_engine
from kkplot.kkengines.base import kkplot_plotmethod as kkplot_plotmethod
from kkplot.kkplot_dviplot import kkplot_dviplot as kkplot_dviplot

from kkplot.kkutils.log import *
from kkplot.kkutils import writer as kkplot_writer

from kkplot.kkengines.pythonbase import *
from kkplot.kkengines.pythonvtk.plotmethods import *

import sys
import time

class kkplot_engine_vtk( kkplot_engine_base_python) :
    def  __init__( self, _conf=None, _dviplot=None) :
        super( kkplot_engine_vtk, self).__init__( "vtk", _conf, _dviplot)

        kkplot_plotmethods = dict( \
            time_surface=kkplot_pythonvtk_time_surface, \
            time_volume=kkplot_pythonvtk_time_volume, \
            none=None)
        self.add_plotmethods( kkplot_plotmethods)

    def  new( self, _conf, _dviplot) :
        enginevtk = kkplot_engine_vtk( _conf, _dviplot)
        enginevtk.new_writer()
        return  enginevtk

    def  __str__( self) :
        return  self.name;

    def  help( self) :
        help_text = 'available graph types: { %s }' \
            % ( ', '.join( [ '\'%s\'' % ( plotmethod) for plotmethod in self.plotmethods]))
        return help_text

    def  generate( self) :

        self.generate_preamble()
        self.generate_plots()
        self.generate_postamble()

        return 0

    def  write( self, _target=None) :
        self.writer.write( _target=_target)

    def generate_plots( self) :

        graphmethods = self._generate_graphmethods( self.make_graph)
        if len( graphmethods) == 0 :
            return

        self.generate_plots_createvtk()
        self.writer.newline()

        self.python_plots_graphmethodcalls( graphmethods)
        self.writer.newline()

        self.writer.append( KKPLOT_RUN_USER_CODE)

        self.writer.newline()

    def make_graph( self, _graphmethod, _graph, _plot, _graphcolumns, _auxgraphcolumns) :
        graph_method_call = _graphmethod( self, _graph.graphid, _graph, _graphcolumns, _auxgraphcolumns, \
            graphresults='graphresults', dataframe='kkdataframes["%s"]' % ( _graph.graphid), outputdir=self.dviplot.outputfile)
        return  graph_method_call

    def _import_user_module( self) :
        self.writer.appendnl( 'user_code_available = False')

    def generate_plots_createvtk( self) :
        self.writer.appendnl( '\n\ndef create_vtk() :')

    def generate_preamble( self) :
        self.python_preamble()
        self.writer.appendnl( 'import vtk as vtk')
        self.writer.appendnl( 'import math as math')
        self.writer.newline()
        self.python_addhelpers( [])
        self.writer.newline()

        self._import_user_module()

    def generate_postamble( self) :
        self.writer.appendnl( 'if __name__ == "__main__" :')
        self.writer.iappendnl( 1, 'create_vtk()\n')
        self.python_postamble()

__kkplot_engine_vtk_factory = kkplot_engine_vtk()

