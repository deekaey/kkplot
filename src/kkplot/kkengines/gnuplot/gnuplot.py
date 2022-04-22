
## example call
## python kkplot.py -E gnuplot

from kkplot.kkengines.base import kkplot_engine as kkplot_engine
from kkplot.kkplot_dviplot import kkplot_dviplot as kkplot_dviplot

from kkplot.kkutils.log import *
from kkplot.kkutils import writer as kkplot_writer

import sys
import pandas
import time

def kkplot_gnuplot_time_line( self, _plotcmd, _graph, _graphcolumns, _auxgraphcolumns, _datafile, _columnmap) :

    datafile = str( _datafile)
    plotcmds = list()

    if _plotcmd is None :
        plotcmd = 'set datafile separator ","\nplot'
    else :
        plotcmd = str( _plotcmd) + ','

## TODO memorize plot id, to continue plot line
    for column_id in _graphcolumns :
        plotcmds.append( '"%s" using %d:%d %s ti "%s"' \
            % ( datafile, _columnmap['time'], _columnmap['%s' % ( column_id)],
                self.get_kind( _graph), _graph.get_property( 'label.%s' % ( column_id))))
        datafile = ''
## TODO need comma!
    return plotcmd + ' ' + ','.join( plotcmds)

class kkplot_engine_gnuplot( kkplot_engine) :
    def  __init__( self, _conf=None, _dviplot=None) :
        super( kkplot_engine_gnuplot, self).__init__( "gnuplot", _conf, _dviplot)

        self.wrtr = None
        self.plotcmds = dict()

        kkplot_plotmethods = dict( \
            time_line=kkplot_gnuplot_time_line,
            time_points=kkplot_gnuplot_time_line,
            none=None)
        self.add_plotmethods( kkplot_plotmethods)


    def  new( self, _conf, _dviplot) :
        engine_gnuplot = kkplot_engine_gnuplot( _conf, _dviplot)
        engine_gnuplot.new_writer()
        return  engine_gnuplot
    @property
    def writer( self) :
        return  self.wrtr
    def new_writer( self) :
        if self.wrtr is None :
            self.wrtr = kkplot_writer( _stream=None, _mode='gnuplot')
        return  self.wrtr

    def  __str__( self) :
        return  self.name;

    def  help( self) :
        return "no help"

    def get_columnmap( self, _graphid) :
        try :
            data = pandas.read_csv( self.dviplot.datapool_filename( _graphid), header=0, parse_dates=['time'], \
                index_col=False, keep_date_col=True, na_values=['na','nan','-99.99'], sep=',')
        except :
            kklog_error( "failed to open datafile  [datafile=%s]" % ( self.dviplot.datapool_filename( _graphid)))
            return None

        columnmap = dict()
        for k, column in enumerate( data.columns) :
            kklog_debug( "map: column=%s, index=%d" % ( column, k+1))
            columnmap[column] = k+1
        del data

        return  columnmap


    def  generate( self) :

        self.generate_preamble()
        self.generate_create_plot()
        self.generate_postamble()

        return 0

    def  write( self, _target=None) :
        self.writer.write( _target=_target)
    @property
    def  suffix( self) :
        return 'gnuplot'

    def generate_create_plot( self) :

        self.generate_terminal( self.dviplot.outputfile)

        self.writer.appendnl( 'set output "%s"' % ( self.dviplot.outputfile))

        self.generate_layout()

        self.writer.appendnl( 'set xdata time')
        self.writer.appendnl( 'set timefmt "%Y-%m-%d"')

        graphmethods = self.generate_plots()
        if len( graphmethods) == 0 :
            return
        self.write_plots( graphmethods)


    def generate_terminal( self, _outputfile) :
        o = _outputfile.lower()
        if o.endswith( '.pdf') :
            self.writer.appendnl( 'set terminal pdfcairo enhanced color size %fin,%fin' % ( self.dviplot.size_x, self.dviplot.size_y))
        elif o.endswith( '.ps') :
            self.writer.appendnl( 'set terminal postscript default')
            self.writer.appendnl( 'set terminal postscript enhanced color colortext size %fin,%fin' % ( self.dviplot.size_x, self.dviplot.size_y))
        elif o.endswith( '.eps') :
            self.writer.appendnl( 'set terminal postscript default')
            self.writer.appendnl( 'set terminal postscript eps enhanced color colortext size %fin,%fin' % ( self.dviplot.size_x, self.dviplot.size_y))
        elif o.endswith( '.png') :
            self.writer.appendnl( 'set terminal png enhanced truecolor size %f,%f #transparent' % ( 100.0*self.dviplot.size_x, 100.0*self.dviplot.size_y))
        elif o.endswith( '.jpg') or o.endswith( '.jpeg') :
            self.writer.appendnl( 'set terminal jpeg enhanced size %f,%f' % ( 100.0*self.dviplot.size_x, 100.0*self.dviplot.size_y))
        elif o.endswith( '.fig') :
            self.writer.appendnl( 'set terminal fig color inches size %f,%f textspecial' % ( self.dviplot.size_x, self.dviplot.size_y))
        elif o.endswith( '.tex') or o.endswith( '.latex') :
            self.writer.appendnl( 'set terminal latex size %fin,%fin' % ( self.dviplot.size_x, self.dviplot.size_y))
        else :
            ## 'pdf' output is default
            return  self.generate_terminal( 'file.pdf')

    def generate_layout( self) :
        figure_title = ''
        if self.dviplot.title :
            figure_title = self.dviplot.title
        self.writer.appendnl( 'set multiplot layout %d,%d scale 1,1 title "%s"' % ( self.dviplot.extent_y, self.dviplot.extent_x, figure_title))
        self.writer.appendnl( 'set lmargin 14')
        self.writer.appendnl( 'set bmargin 4')
        self.writer.appendnl( 'set tmargin 0')
        self.writer.appendnl( 'set rmargin 6')
        self.writer.appendnl( 'set grid')
        self.writer.appendnl( 'set tics out nomirror scale 0.25')
        self.writer.appendnl( 'set border 3')

    def make_graph( self, _graphmethod, _graph, _plot, _graphcolumns, _auxgraphcolumns) :
        columnmap = self.get_columnmap( _graph.graphid)
        if columnmap is None :
            return None

        datafile = self.dviplot.datapool_filename( _graph.graphid)
        plotprops = ''

        ## have we seen plot before?
        plotcmd = None
        if _plot.id in self.plotcmds :
            plotcmd = self.plotcmds[_plot.id]
        else :
            if _plot.title :
                plotprops += 'set title "%s" enhanced\n' % ( _plot.title)
            if _plot.get_property( 'ylabel') :
                plotprops += 'set ylabel "%s" enhanced\n' % ( _plot.get_property( 'ylabel'))
            if _plot.get_property( 'xlabel') :
                plotprops += 'set xlabel "%s" enhanced\n' % ( _plot.get_property( 'xlabel'))
            ## TODO
            plotprops += 'set key top right horizontal box Left samplen 0.5 reverse\n'

        graphmethod = _graphmethod( self, plotcmd,
            _graph, _graphcolumns, _auxgraphcolumns, datafile, columnmap)
        self.plotcmds[_plot.id] = plotprops + graphmethod
        return  _plot.id

    def generate_plots( self) :
        return  self._generate_graphmethods( self.make_graph)
        
    def write_plots( self, _graphmethods) :
        plots = list()
        ## uniquify plot calls
        for graphmethod in _graphmethods :
            if graphmethod.methodcall not in [ '%s' % plot.methodcall for plot in plots ] :
                plots.append( graphmethod)
        ## write plot calls
        for plot in plots :
            graphid = plot.graph.graphid
            if self.dviplot.series_exists( graphid) :
                self.writer.newline()
                self.writer.appendnl( self.plotcmds[plot.methodcall])
        self.writer.newline()

    def generate_preamble( self) :
        self.writer.appendnl( '# vim: ft=gnuplot')
        self.writer.appendnl( '## generated by kkplot on %s\n' % ( time.strftime( '%Y, %b. %d %H:%M')))

    def generate_postamble( self) :
        self.writer.appendnl( 'unset multiplot')
        self.writer.appendnl( 'unset output')

        self.writer.appendnl( '\n')

    def get_kind( self, _graph) :
        gkind = _graph.kind
        lw = str( _graph.get_property( 'linewidth', 1.0))
        if lw == 0 :
            lw = 'variable'
        if gkind == 'standard' or gkind == 'line' or gkind == 'lines' :
            return 'with lines linewidth %s' % ( lw)
        elif gkind == 'point' or gkind == 'points' :
            return 'with points pointsize %s' % ( lw)
        elif gkind == 'bar' :
            return 'with boxes'
        elif gkind == 'stack' or gkind == 'stacked' or gkind == 'area' :
            return ''

        kklog_warn( 'unsupported graph type "%s"' % gkind)
        return None




__kkplot_engine_gnuplot_factory = kkplot_engine_gnuplot()

