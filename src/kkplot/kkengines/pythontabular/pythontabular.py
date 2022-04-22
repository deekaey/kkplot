
## example call
## python kkplot.py -E tabular examples/kkplot-demo-tabular.yaml
##
## supported output formats:
##  csv, tex

from kkplot.kkengines.base import kkplot_engine as kkplot_engine
from kkplot.kkengines.base import kkplot_plotmethod as kkplot_plotmethod
from kkplot.kkplot_dviplot import kkplot_dviplot as kkplot_dviplot

from kkplot.kkutils.log import *
from kkplot.kkutils import writer as kkplot_writer

from kkplot.kkengines.pythonbase import *
from kkplot.kkengines.pythontabular.plotmethods import *

import sys

class kkplot_engine_tabular( kkplot_engine_base_python) :
    def  __init__( self, _conf=None, _dviplot=None) :
        super( kkplot_engine_tabular, self).__init__( "tabular", _conf, _dviplot)

        kkplot_plotmethods = dict( \
            time_fitness=kkplot_pythontabular_time_fit, \
            time_match=kkplot_pythontabular_time_match, \
            none=None)
        self.add_plotmethods( kkplot_plotmethods)

    def  new( self, _conf, _dviplot) :
        enginetabular = kkplot_engine_tabular( _conf, _dviplot)
        enginetabular.new_writer()
        return  enginetabular

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
        self.wrtr.write( _target=_target)

    def generate_plots( self) :

        graphmethods = self._generate_graphmethods( self.make_graph)
        if len( graphmethods) == 0 :
            return

        self.generate_plots_createtabular()
        self.wrtr.newline()

        self.python_plots_graphmethodcalls( graphmethods)
        self.wrtr.newline()

        self.python_tabular_tables()
        self.wrtr.newline()

        self.wrtr.append( KKPLOT_RUN_USER_CODE)

        self.wrtr.newline()

    def make_graph( self, _graphmethod, _graph, _plot, _graphcolumns, _auxgraphcolumns) :
        graph_method_call = _graphmethod( self, _graph.graphid, _graph, _graphcolumns, _auxgraphcolumns, \
            graphresults='graphresults', dataframe='kkdataframes["%s"]' % ( _graph.graphid), outputdir=self.dviplot.outputfile)
        return  graph_method_call

    def python_tabular_tables( self) :
## TODO  not very beautiful..
        self.wrtr.iappendnl( 1, 'plottables = dict()')
        self.wrtr.iappendnl( 1, 'plottables_properties = dict()')
        self.wrtr.iappendnl( 1, 'plottables_order = list()')
        for graph, plot in self.dviplot :
            self.wrtr.iappendnl( 1, 'if "%s" not in plottables.keys() :' % ( plot.id))
            self.wrtr.iappendnl( 2, 'plottables_order.append( "%s")' % ( plot.id))
            self.wrtr.iappendnl( 2, 'plottables["%s"] = list()' % ( plot.id))
            K = plot.get_kindproperties
            if K :
                self.wrtr.iappendnl( 2, 'plottables_properties["%s"] = { %s }' % ( plot.id, \
                    ','.join( [ '"%s":%s' % ( str(k), self._stringify(v)) for k, v in zip( K.keys(), K.values())])))
            else :
                self.wrtr.iappendnl( 2, 'plottables_properties["%s"] = dict()' % ( plot.id))
            K = graph.properties
            if K :
                self.wrtr.iappendnl( 2, 'plottables_properties["%s"] = { %s }' % ( plot.id, \
                    ','.join( [ '"%s":%s' % ( str(k), self._stringify(v)) for k, v in zip( K.keys(), K.values())])))
            else :
                self.wrtr.iappendnl( 2, 'plottables_properties["%s"] = dict()' % ( plot.id))
            self.wrtr.iappendnl( 2, 'plottables_properties["%s"].update( {"title": "%s"} )' % ( plot.id, plot.title))

            self.wrtr.iappendnl( 2, 'headers = %s' % ( graph.get_property('header', None)))
            self.wrtr.iappendnl( 2, 'if headers is not None :')
            self.wrtr.iappendnl( 3, 'plottables_properties["%s"].update({"headers": headers})' % ( plot.id))

            self.wrtr.iappendnl( 1, 'if isinstance(  graphresults["%s"][0], list) :' % ( graph.graphresult))
            self.wrtr.iappendnl( 2, 'for result in graphresults["%s"] :' % ( graph.graphresult))
            self.wrtr.iappendnl( 3, 'plottables["%s"].append( result)' % ( plot.id))
            self.wrtr.iappendnl( 1, 'else :')
            self.wrtr.iappendnl( 2, 'plottables["%s"].append( graphresults["%s"])' % ( plot.id, graph.graphresult))
        
        self.wrtr.iappendnl( 1, 'doc = SimpleDocTemplate("%s", pagesize=letter)' % ( self.dviplot.outputfile))
        self.wrtr.iappendnl( 1, 'table_elements = []')
        self.wrtr.iappendnl( 1, 'word_document = Document()')
        self.wrtr.iappendnl( 1, 'document_name = "Table"')

        self.wrtr.iappendnl( 1, 'for tbl in plottables_order :')
        self.wrtr.iappendnl( 2, 'P = plottables_properties[tbl] if tbl in plottables_properties else dict()')
        self.wrtr.iappendnl( 2, 'table = tab.tabulate( plottables[tbl]' + ', '
#            +'''headers=( %s) % ( ",".join( \'"%s"\' % ( P.get( "headers", "").split(";"))))''' + ', '
            +'headers=P.get( "headers", [])' + ', '
            +'tablefmt=P.get( "format", "plain")' + ', '
            +'numalign=P.get( "decimalalign", "left")' + ', '
            +'floatfmt=P.get( "floatformat", "g")'
            +')')
## TODO write to output
        self.wrtr.iappendnl( 2, 'sys.stdout.write( "%s\\n" % ( table))')


        self.wrtr.iappendnl( 2, 'rows=[plottables_properties[tbl]["headers"]]')
        self.wrtr.iappendnl( 2, 'rows[0].insert(0,"")')
        self.wrtr.iappendnl( 2, 'for row in plottables[tbl]:')
        self.wrtr.iappendnl( 3, 'rows.append(row[:])')
        self.wrtr.iappendnl( 2, 't=Table(rows)')

        self.wrtr.iappendnl( 2, 't.hAlign = "LEFT"')
        self.wrtr.iappendnl( 2, 't.spaceBefore =  10')
        self.wrtr.iappendnl( 2, 't.spaceAfter = 10')

        self.wrtr.iappendnl( 2, 't.setStyle(TableStyle([("BOX", (0,0), (-1,-1), 0.5, colors.black), ("INNERGRID", (0,0), (-1,-1), 0.5, colors.black)]))')
        self.wrtr.iappendnl( 2, 'table_elements.append( Paragraph( plottables_properties[tbl]["title"]))')
        self.wrtr.iappendnl( 2, 'table_elements.append(t)')
        

        self.wrtr.iappendnl( 2, 'word_doc = word_document.add_paragraph(plottables_properties[tbl]["title"])')
        self.wrtr.iappendnl( 2, 'word_tab = word_document.add_table(0, 0)')
        self.wrtr.iappendnl( 2, 'word_tab.style = "TableGrid"')
        self.wrtr.iappendnl( 2, 'column_width = 5')
        self.wrtr.iappendnl( 2, 'for col in range(len(plottables[tbl][0])):')
        self.wrtr.iappendnl( 3, 'word_tab.add_column(Cm(column_width))')
        self.wrtr.iappendnl( 2, 'for r in range(len(plottables[tbl])):')
        self.wrtr.iappendnl( 3, 'word_tab.add_row()')
        self.wrtr.iappendnl( 3, 'row = word_tab.rows[r]')
        self.wrtr.iappendnl( 3, 'for c in range(len(plottables[tbl][r])):')
        self.wrtr.iappendnl( 4, 'row.cells[c].text = str(plottables[tbl][r][c])')

        self.wrtr.iappendnl( 1, 'word_document.save(document_name + ".docx")')
        self.wrtr.iappendnl( 1, 'doc.build(table_elements)')

    def generate_plots_createtabular( self) :
        self.wrtr.appendnl( '\n\ndef create_tabular() :')

    def generate_preamble( self) :
        self.python_preamble()
        self.wrtr.appendnl( 'import math as math')
        self.wrtr.appendnl( 'import numpy as numpy')
        self.wrtr.appendnl( 'import tabulate as tab')
        self.wrtr.appendnl( 'from reportlab.lib import colors')
        self.wrtr.appendnl( 'from reportlab.lib.pagesizes import letter')
        self.wrtr.appendnl( 'from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph')
        self.wrtr.appendnl( 'from docx import Document')
        self.wrtr.appendnl( 'from docx.shared import Cm, Pt')
        self.wrtr.newline()
        self.python_addhelpers( [])
        self.wrtr.newline()

    def generate_postamble( self) :
        self.wrtr.appendnl( 'if __name__ == "__main__" :')
        self.wrtr.iappendnl( 1, 'create_tabular()\n')
        self.python_postamble()

__kkplot_engine_tabular_factory = kkplot_engine_tabular()


