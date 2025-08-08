
## example call
## python kkplot.py -E bokeh examples/config.yml
##
## supported output formats:
##  eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff
from kkplot.kkengines.base import kkplot_engine as kkplot_engine
from kkplot.kkengines.base import kkplot_plotmethod as kkplot_plotmethod
from kkplot.kkplot_dviplot import kkplot_dviplot as kkplot_dviplot

from kkplot.kkutils.log import *
from kkplot.kkutils import writer as kkplot_writer

from kkplot.kkengines.pythonbokeh.plotmethods import *

import sys
import time


KKPLOT_MATPLOTLIB_TIMEDELTA = '''
class kkplot_matplotlib_timedelta( object) :
    def __init__( self, _timedelta) :
        self._td = _timedelta
        
    @property
    def seconds( self) :
        return float( self._td.days * 86400 + self._td.seconds)
    @property
    def minutes( self) :
        return float( self._td.days * 1440 + self._td.seconds//60)
    @property
    def hours( self) :
        return float( self._td.days * 24 + self._td.seconds//3600)
    @property
    def days( self) :
        return float( self._td.days)
'''

KKPLOT_MATPLOTLIB_TIMEPERIOD = '''
class kkplot_matplotlib_timeperiod( object) :
    def __init__( self, _timedelta) :
        self._td = kkplot_matplotlib_timedelta( _timedelta)

    @property
    def seconds( self) :
        return self._td.seconds + 1.0
    @property
    def minutes( self) :
        return self._td.minutes + 1.0
    @property
    def hours( self) :
        return self._td.hours + 1.0
    @property
    def days( self) :
        return self._td.days + 1.0
'''

KKPLOT_REMOVE_NONE = '''
def kkplot_remove_none( _list):
    b = []
    for sublist in _list:
        cleaned = [elem for elem in sublist if elem is not None]
        if len(cleaned):  # anything left?
            b.append(cleaned)
    return b
'''

class kkplot_engine_bokeh( kkplot_engine) :
    def  __init__( self, _conf=None, _dviplot=None) :
        super( kkplot_engine_bokeh, self).__init__( "bokeh", _conf, _dviplot)

        self.W = None

        kkplot_plotmethods = dict( \
            time_line=kkplot_pythonbokeh_time_line, \
            time_bars=kkplot_pythonbokeh_time_bars, \
            time_points=kkplot_pythonbokeh_time_points, \
            time_points_errors=kkplot_pythonbokeh_time_points_errors, \
            time_regressionpoint=kkplot_pythonbokeh_time_regressionpoint, \
            time_regressionline=kkplot_pythonbokeh_time_regressionline, \
            none=None)
        self.add_plotmethods( kkplot_plotmethods)

    @property
    def writer( self) :
        return self.W

    def  new( self, _conf, _dviplot) :
        enginebokeh = kkplot_engine_bokeh( _conf, _dviplot)
        enginebokeh.W = kkplot_writer( _stream=None, _mode='python')
        return  enginebokeh

    def  __str__( self) :
        return  self.name;

    def  help( self) :
        help_text = 'available graph types: { %s }' \
            % ( ', '.join( [ '\'%s\'' % ( plotmethod) for plotmethod in self.plotmethods]))
        return help_text

    def  generate( self) :

        self.generate_preamble( self._dviplot)
        self.generate_plots()
        self.generate_postamble()

        return 0

    def  write( self, _target=None) :
        self.W.write( _target=_target)
    @property
    def suffix( self) :
        return 'py'

    def generate_plots( self) :

        graphmethods = self.generate_plots_graphmethods()
        if len( graphmethods) == 0 :
            return

        self.generate_plots_auxiliarycode()
        self.generate_plots_createfigure()

        self.W.iappendnl( 0, '')

        self.generate_plots_graphmethodcalls( graphmethods)
        self.generate_plots_setplotproperties()
        self.generate_plots_setgraphproperties()


        self.generate_plots_writefigure()

        self.W.newline()
        self.W.iappendnl( 1, 'return None, None')

    def generate_plots_auxiliarycode( self) :
        pass

    def generate_plots_createfigure( self) :
        self.W.appendnl( '\n\ndef create_figure() :')
        self.generate_layout()

    def generate_layout( self) :
        self.W.iappendnl( 1, '')
        self.W.iappendnl( 1, 'kkaxes = dict()')
        define_layout = True
        for graph, plot in self.dviplot :
            ax_index = self._axis_index( plot)
            ax_position = self._axis_position( plot)
            plotheight = graph.get_property( 'plotheight', 300)
            if graph.kind in ['regressionpoint', 'regressionline'] :
                self.W.iappendnl( 1, 'if bokeh_version >= "3.0.0":')
                self.W.iappendnl( 2, 'kkaxes["%s"] = figure(x_axis_type="linear", height=%d)' % ( ax_index, plotheight))
                self.W.iappendnl( 1, 'else:')
                self.W.iappendnl( 2, 'kkaxes["%s"] = figure(x_axis_type="linear", plot_height=%d)' % ( ax_index, plotheight))
            else:
                self.W.iappendnl( 1, 'if bokeh_version >= "3.0.0":')
                self.W.iappendnl( 2, 'kkaxes["%s"] = figure(x_axis_type="datetime", height=%d)' % ( ax_index, plotheight))
                self.W.iappendnl( 1, 'else:')
                self.W.iappendnl( 2, 'kkaxes["%s"] = figure(x_axis_type="datetime", plot_height=%d)' % ( ax_index, plotheight))
            if define_layout:
                self.W.iappendnl( 1, 'kklayout = [[None for x in range(%d)] for y in range(%d)]' %(self.dviplot.extent_x, self.dviplot.extent_y) )
                define_layout = False
            self.W.iappendnl( 1, 'kklayout[%s][%s] = kkaxes["%s"]' \
                % ( ax_position.split(',')[0], ax_position.split(',')[1], ax_index))            
    def generate_plots_graphmethods( self) :
        self.W.iappendnl( 0, '')

        graph_method_calls = list()

        ## add plots
        for graph, plot in self.dviplot :
            ax_index = self._axis_index( plot)

            if graph.domain is None :
                continue

            graph_columns = list()
            auxialiary_columns = list()
            for dataselect in graph :
                aux_column_ids = graph.referenceids( dataselect)
                column_id = []
                if len( aux_column_ids) > 0 :
                    column_id = aux_column_ids.pop( 0) ## discard column_id

                graph_columns.append( column_id)
                auxialiary_columns.append( aux_column_ids)
                #kklog_debug( 'columns = %s' % ( ';'.join( [column_id]+aux_column_ids)))

                column_ids = graph.referenceids( dataselect)
                column_names = graph.names
                add_datalabel = graph.get_property( 'datalabel', True)
                for ( column_id, column_name) in zip( column_ids, column_names) :
                    graph_label = graph.label( column_name)
                    if graph_label is None :
                        column_label = None
                    elif add_datalabel :
                        column_label = '%s%s' % ( graph_label, graph.datalabel( dataselect, ' [%s]'))
                    else :
                        column_label = '%s' % ( graph_label)
                    graph.add_properties( { 'label.%s' % ( column_id): column_label})

            plotmethod = self.get_plotmethod( graph)
            if plotmethod :
                graph_method_call = plotmethod( self, graph.graphid, graph, ax_index, graph_columns, auxialiary_columns, \
                    graphresults='graphresults', axes='kkaxes', \
                    dataframe='kkdataframes["%s"]' % ( graph.graphid), figure='kkfigures', dviplot=self._dviplot)
                if graph_method_call is None :
                    kklog_error( 'failed to generate code for graph "%s"' % ( graph.graphid))
                    return list()
                graph_method_calls.append( kkplot_plotmethod( graph, graph_method_call))
            else :
                pass

        return  graph_method_calls

    def as_attr( self, _id, _obj, _propertyname, _propertydefaultvalue) :
        propertyvalue = getattr( _obj, _propertyname, _propertydefaultvalue)
        return ( _id, _propertyname, self._stringify( propertyvalue))

    def generate_plots_graphmethodcalls( self, _graphmethods) :
        w = self.W.iappendnl

        w( 0, '')
        w( 1, 'graphresults = dict()')
        w( 1, 'kkdataframes = dict()')

        seriesopts = dict( time=', parse_dates=["time"], index_col=1', space='', non='')
        delim = self._conf.tmpdata_column_delim
        ## add graphs
        for graphmethod in _graphmethods :
            graphid = graphmethod.graph.graphid
            if self.dviplot.series_exists( graphid) :
                w( 1, 'try :')
                w( 2, 'kkdataframes["%s"] = pandas.read_csv( "%s", ' % ( graphid, self.dviplot.datapool_filename( graphid)) +
                    'header=0, na_values=["na"], sep="%s"' % ( delim) + seriesopts[graphmethod.graph.domainkind] + ')')
                w( 1, 'except :')
                w( 2, r'sys.stderr.write( "failed to open datafile  [datafile=%s]\n")' % ( self.dviplot.datapool_filename( graphid)))
                w( 2, r'sys.exit( 13)')

            w( 1, 'graphresults["%s"] = \\' % ( graphmethod.graph.graphresult))
            w( 2, graphmethod.methodcall)

    def generate_plots_setgraphproperties( self) :
        return 

    def generate_plots_setplotproperties( self) :
        w = self.W.iappendnl
        for plot in self.dviplot.plots :
            axis = self._axis_index( plot)
            w( 1, '')
            #w( 1, '(x0, x1), (y0, y1) = kkaxes["%s"].get_xlim(), kkaxes["%s"].get_ylim()' % ( axis, axis))
            self.generate_plots_setplotproperty( plot)        
        return

    def generate_plots_setplotproperty( self, _plot) :

        self._setplotproperty( _plot, 'xlabel', 'xaxis.axis_label', _value=None, _bool=None, _tex=True)
        #self._setplotproperty( _plot, 'xlabelfontsize', 'xaxis.label.set_size')
        self._setplotproperty( _plot, 'ylabel', 'yaxis.axis_label', _value=None, _bool=None, _tex=True)
        #self._setplotproperty( _plot, 'ylabelfontsize', 'yaxis.label.set_size')

        for axis in ['xaxis', 'yaxis']:
            self._setplotproperty( _plot, 'desired_num_ticks', f'{axis}.ticker', _value=4, _bool=None, _tex=False,
                                   _fun='BasicTicker', _fun_keyword='desired_num_ticks')
        #kkaxes["trace_gas_CH4"].yaxis.ticker = BasicTicker(desired_num_ticks=5)

        _plot.add_properties( dict( title=''))
        if _plot.title is not None :
            _plot.add_properties( dict( title=_plot.title))
        self._setplotproperty( _plot, 'title', 'title.text', _value=None, _bool=None, _tex=True)


        #kkaxes["water_10"].x_range.start = int( datetime.datetime.strptime("2006-01-01", '%Y-%m-%d').timestamp())*1000
        #kkaxes["water_10"].x_range.end   = int( datetime.datetime.strptime("2006-01-01", '%Y-%m-%d').timestamp())*1000
        w = self.W.iappendnl
        w( 1, 'def convert_to_integer( _d) :')
        w( 2, 'if type( _d) == str :')
        w( 3, 'return int( datetime.datetime.strptime(_d, "%Y-%m-%d").timestamp())*1000')
        w( 2, 'return _d')
        self._setplotproperty( _plot, 'xlimitlow', 'x_range.start',  _value=None, _bool=None, _tex=False, _fun='convert_to_integer')
        self._setplotproperty( _plot, 'xlimithigh', 'x_range.end',  _value=None, _bool=None, _tex=False, _fun='convert_to_integer')
        self._setplotproperty( _plot, 'ylimitlow,ylimithigh', 'y_range',  _value=None, _bool=None, _tex=False, _fun='Range1d')
        #self._setplotproperty( _plot, 'zlimitlow,zlimithigh', 'z_rangeRange1d')
        return

    def _setplotproperty( self, _plot, _props, _setter, _value=None, _bool=None, _tex=False, _fun='', _fun_keyword='') :
        axis = self._axis_index( _plot)
        self.__setplotproperty( _plot, axis, _props, _setter, _value, _bool, _tex, _fun, _fun_keyword)

    def __setplotproperty( self, _plot, _axis, _props, _setter, _value=None, _bool=None, _tex=False, _fun='', _fun_keyword='') :
        self.W.comment_off()
        values = list()
        for prop in _props.split( ',') :
            if _plot.get_property( prop) is not None :
                if _bool is not None and _plot.get_property( prop) != _bool :
                    self.W.comment_on()
                #values.append( _value if _value is not None else _plot.get_property( prop))
                values.append( _plot.get_property( prop))
            elif _value is not None:
                values.append( _value)
            else:
                values = ['<%s>' % ( _props)]
                self.W.comment_on()
                break

        if _fun_keyword != '':
            _fun_keyword = _fun_keyword+'='

        if _tex :
            property_code = 'kkaxes["%s"].%s = %s(%sLatexNodes2Text().latex_to_text( %s))' \
                % ( _axis, _setter, _fun, _fun_keyword, ', '.join( [ self._stringify( value) for value in values]))
        else :
            property_code = 'kkaxes["%s"].%s = %s(%s%s)' \
                % ( _axis, _setter, _fun, _fun_keyword, ', '.join( [ self._stringify( value) for value in values]))

        self.W.iappendnl( 1, '%s' % ( property_code))
        self.W.comment_off()

    def _setplotxyticklabelsrotation( self, _plot) :
        ax_index = self._axis_index( _plot)
        if _plot.get_property( 'xticklabelsrotation') is None :
            self.W.comment_on()
        self.W.iappendnl( 1, 'for ticklabel in kkaxes["%s"].%s() :' % ( ax_index, 'get_xticklabels'))
        self.W.iappendnl( 2, 'ticklabel.set_rotation( %s)' % ( str( _plot.get_property( 'xticklabelsrotation', '"<float>"'))))
        self.W.comment_off()

        if _plot.get_property( 'yticklabelsrotation') is None :
            self.W.comment_on()
        self.W.iappendnl( 1, 'for ticklabel in kkaxes["%s"].%s() :' % ( ax_index, 'get_yticklabels'))
        self.W.iappendnl( 2, 'ticklabel.set_rotation( %s)' % ( str( _plot.get_property( 'yticklabelsrotation', '"<float>"'))))
        self.W.comment_off()

    def generate_plots_writefigure( self) :
        self.W.iappendnl( 0, '')

        #tl_left, tl_bottom, tl_right, tl_top = ( 0.0, 0.0, 1.0, 1.0)
        #self.W.iappendnl( 1, 'p = gridplot(kklayout, plot_width=%d, plot_height=%d, sizing_mode="scale_width")' % (self.dviplot.size_x*30, self.dviplot.size_y*20))
        #self.W.iappendnl( 1, 'p = layout(kkplot_remove_none(kklayout), sizing_mode="stretch_width")')
                
        h = self.dviplot.get_property( 'plotheight', 300)
        w = self.dviplot.get_property( 'plotwidth', h)
            
        self.W.iappendnl( 1, 'kklayout = [[x for x in sub_list if x is not None] for sub_list in kklayout]')
        if self.dviplot.get_property( 'layout', 'gridplot') == 'gridplot':
            self.W.iappendnl( 1, 'p = gridplot( kklayout, width=%d, height=%d)' %(w,h))
        else:
            self.W.iappendnl( 1, 'p = layout( kklayout, sizing_mode="stretch_width")')
        #tl_top = 0.95
        self.W.iappendnl( 1, 'sys.stderr.write( \'writing "%s.html"...\\n\')' % ( self.dviplot.outputfile.split(".")[0]))
        if self.dviplot.components :
            self.W.iappendnl( 1, 'script, div = components( p)')
            self.W.iappendnl( 1, 'output_file = open( "%s.html", "w")' % ( self.dviplot.outputfile.split(".")[0]))
            self.W.iappendnl( 1, 'output_file.write( script)')
            self.W.iappendnl( 1, 'output_file.write( div)')
            self.W.iappendnl( 1, 'output_file.close()')
        else :                
            self.W.iappendnl( 1, 'output_file( "%s.html")' % ( self.dviplot.outputfile.split(".")[0]))

            if self.dviplot.title :
                font_size = "'font-size:200%'"
                self.W.iappendnl( 1, 'division_content=Div(text="<div style=%s>%s</div>")' % (font_size, self.dviplot.title))
                self.W.iappendnl( 1, 'save( column(division_content, p, sizing_mode="scale_width", margin=(50, 50, 50, 50)))')
            else:
                self.W.iappendnl( 1, 'save(p)')


    def generate_preamble( self, _dviplot) :
        self.W.appendnl( '# vim: ft=python')
        self.W.appendnl( '## generated by kkplot on %s\n' % ( time.strftime( '%Y, %b. %d %H:%M')))
        self.W.appendnl( 'import sys as sys')
        self.W.appendnl( 'import math as math')
        self.W.appendnl( 'import datetime as datetime')
        self.W.appendnl( 'import pandas as pandas')
        self.W.appendnl( 'import numpy as numpy')
        self.W.appendnl( 'import matplotlib as matplotlib')
        self.W.appendnl( 'import matplotlib.cm as matplotlib_colormap')
        self.W.appendnl( 'from bokeh.io import output_file, save')
        self.W.appendnl( 'from bokeh.layouts import gridplot, column, row, layout')
        self.W.appendnl( 'from bokeh.plotting import figure')
        self.W.appendnl( 'from bokeh.models.annotations import Title, Label')
        self.W.appendnl( 'from bokeh.models import Range1d, Div, BasicTicker')
        self.W.appendnl( 'from bokeh.embed import components')
        self.W.appendnl( 'from bokeh.models import ColumnDataSource, Whisker')
        self.W.appendnl( 'import bokeh')
        self.W.appendnl( 'bokeh_version = bokeh.__version__')
        self.W.appendnl( 'from bokeh.palettes import Category10')
        self.W.appendnl( 'bokeh_colors = Category10[10]')

        self.W.appendnl( 'from pylatexenc.latex2text import LatexNodes2Text')
        self.W.appendnl( '')

        self._import_user_module()

        self.W.appendnl( KKPLOT_MATPLOTLIB_TIMEDELTA)
        self.W.appendnl( KKPLOT_MATPLOTLIB_TIMEPERIOD)
        self.W.appendnl( KKPLOT_REMOVE_NONE)

        self.W.appendnl( '')

    def generate_postamble( self) :
        self.W.appendnl( '\n')
        self.W.appendnl( 'if __name__ == "__main__" :')
        self.W.iappendnl( 1, 'kkfigures, kkaxes = create_figure()\n')

    def _import_user_module( self) :
        self.W.iappendnl( 0, 'user_code_available = False')
## sk:off        import os
## sk:off
## sk:off        o = self.dviplot.outputfile.strip()
## sk:off        o = o.replace( '/', os.sep)
## sk:off        o = o.replace( '\\', os.sep)
## sk:off        o_path, o_file = os.path.split( o)
## sk:off        if not o_path == '' :
## sk:off            self.W.iappendnl( 0, 'import sys')
## sk:off            self.W.iappendnl( 0, 'sys.path.insert( 0, "%s")' % ( os.path.abspath( o_path)))
## sk:off        module_name = self._canonicalize_name( o_file)
## sk:off        self.W.iappendnl( 0, 'user_code_available = True')
## sk:off        self.W.iappendnl( 0, 'try:')
## sk:off        self.W.iappendnl( 1, 'import %s as user_code' % ( module_name))
## sk:off        self.W.iappendnl( 1, 'print( "seeing user changes, using them")')
## sk:off        self.W.iappendnl( 0, 'except ImportError : #as import_error :')
## sk:off        self.W.iappendnl( 1, '## no user code')
## sk:off        self.W.iappendnl( 1, '#print( "ImportError: %s" % ( import_error))')
## sk:off        self.W.iappendnl( 1, 'user_code_available = False')
## sk:off        self.W.iappendnl( 0, '')

    def _axis_index( self, _plot) :
        return '%s' % ( _plot.id)
    def _axis_position( self, _plot) :
        return '%s,%s' % ( _plot.position_y, _plot.position_x)


    def _canonicalize_name( self, _name) :
        validchars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789'
        canonicalized_name = ''
        for c in _name :
            if not c in validchars :
                canonicalized_name += '_'
            else :
                canonicalized_name += c

        return canonicalized_name

    def _make_args( self, _commas, **_kwargs) :
        args = ', '.join([ '%s=%s' % ( k, self._stringify( v)) for ( k, v) in zip( _kwargs.keys(), _kwargs.values()) if v is not None])
        if args == '' :
            pass
        elif _commas == 'l' :
            args = ', %s' % ( args)
        elif _commas == 'r' :
            args += ', '
        elif _commas == 'lr' or _commas == 'rl' :
            args = ', %s, ' % ( args)
        return args

    def _make_flabels( self, _columns, _graph, _kwargs) :
        dataframe = _kwargs.get( 'dataframe')
        if dataframe is None :
            return
        from kkengines.pythoncode import fitness
        for column in _columns :
            lbl = self._make_label( column, _graph)
            if not lbl.strip().startswith( '@') :
                continue

            if not ':' in lbl :
                kklog_fatal( 'label format for functions "@F:arg1,arg2,...,argN"')

            lblfunc, lblargs = lbl.split( ':')
            lblfunc = lblfunc[1:]
            lblargs = lblargs.split( ',')

            fitness_fun = getattr( fitness, lblfunc)
            if not fitness_fun :
                kklog_fatal( 'unknown labeling function "%s"' % ( lblfunc))

            subcolumns = self._find_columns( lblargs, _columns)

            self.writer.push_indentlevel()
            lblvar = fitness_fun( self.writer, dataframe, subcolumns[0], subcolumns[1])
            self.writer.pop_indentlevel()

            fitness_fun_name = getattr( fitness, '%s_name' % ( lblfunc))
            if fitness_fun_name is None :
                kklog_fatal( 'no function called "%s_name"' % ( lblfunc))
            _graph.add_properties( { 'label.%s' % ( column): '<NOSTRINGIFY>"%s = %%0.2f" %% ( %s)' % ( fitness_fun_name(), lblvar)})

    def _make_label( self, _column, _graph) :
        lbl = lambda c : _graph.get_property( 'label.%s' % ( c))
        label = '%s' % ( '_nolabel' if lbl(_column) is None else lbl(_column))
        return label
    def _make_labels( self, _columns, _graph, **_kwargs) :
        if len( _kwargs) > 0 :
            self._make_flabels( _columns, _graph, _kwargs)
        labels = '%s' % ( ','.join( \
            [ '"%s":%s' % ( c, self._stringify( self._make_label(c,_graph))) for c in _columns]))
        return labels


    def _stringify( self, _value) :
        if _value is None :
            return 'None'
        elif type( _value) == str :
            if _value.startswith( '<NOSTRINGIFY>') :
                return '%s' % ( _value[13:]) ## TODO len( nostringify)
            return '"%s"' % ( _value)
        else :
            return '%s' % ( str( _value))

    def _toggle( self, _value) :
        kklog_debug( '%s->%s' % ( _value, not _value))
        if _value :
            return not _value
        return _value

    def _get_linestyle( self, _linestyle) :
        if _linestyle == 'solid' or _linestyle == 'line' or _linestyle == 'lines' :
            return '-'
        elif _linestyle == 'point' or _linestyle == 'points' :
            return 'None'
        elif _linestyle == 'dashdot' :
            return '-.'
        elif _linestyle == 'dashed' or _linestyle == 'dash' or _linestyle == 'dashes' :
            return '--'
        elif _linestyle == 'dotted' :
            return ':'

        kklog_warn( 'unsupported line style "%s"' % _linestyle)
        return '-'


__kkplot_engine_bokeh_factory = kkplot_engine_bokeh()

