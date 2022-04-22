
## example call
## python kkplot.py -E pythonwebsite examples/config.yml
##
## supported output formats:
##  html (png graphics)

from kkengines.base import kkplot_engine as kkplot_engine
from kkengines.pythonmatplotlib import kkplot_engine_matplotlib as kkplot_engine_matplotlib
from kkplot_dviplot import kkplot_dviplot as kkplot_dviplot

from kkutils.log import *

import sys
import time

KKPLOT_PYTHONWEBSITE_HTMLOPEN = ''' <!doctype html> <html> '''
KKPLOT_PYTHONWEBSITE_HTMLCLOSE = ''' </html> '''

KKPLOT_PYTHONWEBSITE_HTMLHEAD = ''' <head> <meta charset=\\"utf-8\\"> <title>%s</title> </head> '''
KKPLOT_PYTHONWEBSITE_HTMLFOOT = ''' <footer> <p>%s</p> </footer> '''

class kkplot_engine_pythonwebsite( kkplot_engine) :
    def  __init__( self, _conf=None, _dviplot=None) :
        super( kkplot_engine_pythonwebsite, self).__init__( "pythonwebsite", _conf, _dviplot)

        self.enginebackend = None

    def  new( self, _conf, _dviplot) :
        engine_pythonwebsite = kkplot_engine_pythonwebsite( _conf, _dviplot)

        matplotlibengine = kkplot_engine_matplotlib().new( _conf, _dviplot)
        matplotlibengine.generate_plots_auxiliarycode = engine_pythonwebsite.generate_plots_writer
        matplotlibengine.generate_layout = engine_pythonwebsite.generate_layouts
        matplotlibengine.generate_plots_writefigure = engine_pythonwebsite.generate_plots_writefigures
        matplotlibengine.generate_plots_deleteemptyaxes = engine_pythonwebsite.generate_plots_pass

        ## overwrite plotting methods
        matplotlibengine._kkplot_plot_non_table = engine_pythonwebsite._kkplot_plot_non_table

        engine_pythonwebsite.enginebackend = matplotlibengine

        return  engine_pythonwebsite

    def  __str__( self) :
        return  self.name;

    def  help( self) :
        return "no help"

    def generate( self) :
        rc_generate = self.enginebackend.generate()
        if rc_generate == 0 :
            self.generate_html()
            return 0
        return rc_generate

    def write( self) :
        self.enginebackend.write()

    def generate_plots_pass( self) :
        pass

    def generate_plots_auxiliarycode( self) :
        pass
    def generate_plots_writer( self) :
        import inspect
        writersource = inspect.getsource( type( self.enginebackend.writer))
        self.enginebackend.writer.newline( 3)
        self.enginebackend.writer.iappendnl( 0, 'import sys')
        self.enginebackend.writer.iappendnl( 0, writersource)

    def generate_layouts( self) :
        w = self.enginebackend.writer
        w.iappendnl( 1, '')
        w.iappendnl( 1, 'kkfigures = list()')
        w.iappendnl( 1, 'kkaxes = dict()')
        for plot in self.dviplot.plots :
            ax_index = self.enginebackend._axis_index( plot)
            ax_position = self.enginebackend._axis_position( plot)
            projection = ''
            if plot.get_property( 'projection') :
                projection = ', projection="%s"' % ( plot.get_property( 'projection'))
            w.iappendnl( 1, 'kkfigure = matplotlib_pyplot.figure()')
            w.iappendnl( 1, 'kkfigure.set_size_inches( %f, %f)' % ( self.dviplot.size_x, self.dviplot.size_y))
            w.iappendnl( 1, 'kkfigures.append( ( kkfigure, "%s"))' % ( ax_index))
            w.iappendnl( 1, 'kkaxes["%s"] = kkfigure.gca()' % ( ax_index))

    def generate_plots_writefigures( self) :
        w = self.enginebackend.writer
        w.newline()

        tl_left, tl_bottom, tl_right, tl_top = ( 0.0, 0.0, 1.0, 1.0)
## TODO set website title
#        if self.dviplot.title :
        of = self._outputfile_pattern( self.dviplot.outputfile)
        w.iappendnl( 1, 'for ( j, ( figure, figureid)) in enumerate( kkfigures) :')
        w.iappendnl( 2, 'sys.stderr.write( \'writing "%s" ...\\n\' %% ( j))' % ( of))
        w.iappendnl( 2, 'figure.set_tight_layout( dict( rect=[%.2f, %.2f, %.2f, %.2f])) #pad=1.08, h_pad=2.0, w_pad=2.0' % ( tl_left, tl_bottom, tl_right, tl_top))
        w.iappendnl( 2, 'figure.savefig( "%s" %% ( j), format="%s", dpi=%f, transparent=%s, pad_inches=%f, frameon=%s)' \
                % ( of, 'png', 100, False, 0.1, None))

    def generate_html( self) :
        w = self.enginebackend.writer
        w.newline( 2)
        w.iappendnl( 1, '## create html page')

        of = self._outputfile_pattern( self.dviplot.outputfile)
        figuretitle = '' if self.dviplot.title is None else self.dviplot.title

        plotwidth = 100.0 # / float( self.dviplot.extent_x)
        plotheight = 100.0 # / float( self.dviplot.extent_y)

        w.iappendnl( 1, 'w = kkplot_writer( _stream=None, _mode="html")')
        w.iappendnl( 1, 'w.iappendnl( 0, "%s")' % ( KKPLOT_PYTHONWEBSITE_HTMLOPEN))
        w.iappendnl( 1, 'w.iappendnl( 0, "%s")' % ( KKPLOT_PYTHONWEBSITE_HTMLHEAD % ( figuretitle)))
        w.iappendnl( 1, 'w.iappendnl( 0, "<body>")')
        w.iappendnl( 1, 'w.iappendnl( 1, "<table style=\\"width:100%\\">")')
        w.iappendnl( 1, 'for r in range( %d) : ## rows' % ( self.dviplot.extent_y))
        w.iappendnl( 2, 'w.iappendnl( 2, "<tr>")')
        w.iappendnl( 2, 'for c in range( %d) : ## columns' % ( self.dviplot.extent_x))
        w.iappendnl( 3, 'f_i = r * %d + c' % ( self.dviplot.extent_x))
        w.iappendnl( 3, 'w.iappendnl( 3, "<td>")')

        w.iappendnl( 3, 'if f_i < len( kkfigures) :')
        w.iappendnl( 4, 'f_id = kkfigures[f_i][1]')
        w.iappendnl( 4, 'f = "%s" %% ( f_i)' % ( of))
        w.iappendnl( 4, 'w.iappendnl( 4, "<img width=\\"%f%%%%\\" src=\\"%%s\\" alt=\\"%%s\\">" %% ( f, f_id))' % ( plotwidth)) # plotheight

        w.iappendnl( 3, 'w.iappendnl( 3, "</td>")')
        w.iappendnl( 2, 'w.iappendnl( 2, "</tr>")')

        w.iappendnl( 1, 'w.iappendnl( 1, "</table>")')
        w.iappendnl( 1, 'w.iappendnl( 0, "</body>")')
        generateinfo = 'generated by kkplot on %s' % ( time.strftime( '%Y, %b. %d %H:%M'))
        w.iappendnl( 1, 'w.iappendnl( 0, "%s")' % ( KKPLOT_PYTHONWEBSITE_HTMLFOOT % ( generateinfo)))
        w.iappendnl( 1, 'w.iappendnl( 0, "</html>")')
        w.iappendnl( 1, 'w.write()')


    def _outputfile_pattern( self, _outputfile) :
        ofdotat = _outputfile.rfind( '.')
        of = '%s-%%d' % ( _outputfile)
        if ofdotat != -1 :
            of = _outputfile.split( '.')
            of.pop() ## remove suffix
            of = '%s-%%d.%s' % ( '.'.join( of), 'png')
        return of





    def _kkplot_plot_non_table( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
        axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
        dataframe = _kwargs['dataframe']
        method_call = 'kkplot_plot_non_table_%s( "%s", _dataframe=%s, _axes=%s)' \
            % ( self._canonicalize_name( _id), _id, dataframe, axes)

        self.W.iappendnl( 0, 'def kkplot_plot_non_table_%s( _id, _dataframe, _axes) :' % ( self._canonicalize_name( _id)))
 
        return method_call


__kkplot_engine_pythonwebsite_factory = kkplot_engine_pythonwebsite()

