
from kkutils.log import *
from kkengines.pythoncode import fitness

def kkplot_pythonmatplotlib_time_line( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_time_line_%s( "%s", _dataframe=%s, _axes=%s)' % ( self._canonicalize_name( _id), _id, dataframe, axes)

    columns = _columns
    for auxialiary_columns in _auxialiary_columns :
        columns += auxialiary_columns

    c_lo, c_hi = ( 0.25, 1)

    w = self.W.iappendnl
    w( 0, 'def kkplot_plot_time_line_%s( _id, _dataframe, _axes) :' % ( self._canonicalize_name( _id)))
    w( 1, '_axes.set_gid( _id)')

    w( 1, 'graphlabels = { %s }' % ( self._make_labels( columns, _graph)))

## prototype START
    for column in columns :
        lbl = self._make_label( column, _graph)
        if lbl.strip().startswith( '@') :
            if not ':' in lbl :
                kklog_fatal( 'label format for functions "~F:arg1,arg2,...,argN"')
            lblfunc, lblargs = lbl.split( ':')
            lblfunc = lblfunc[1:]
            lblargs = lblargs.split( ',')

            if lblfunc in [ 'nse', 'r2', 'rmse' ] :
                self.W.push_indentlevel()
                column1, column2 = self._find_columns( lblargs, columns)
                if lblfunc == 'nse' :
                    lblvar = fitness.nse( self.W, '_dataframe', column1, column2)
                    self.W.pop_indentlevel()
                    w( 1, 'graphlabels["%s"] = "NSE = %%0.2f" %% ( %s)' % ( column, lblvar))
                elif lblfunc == 'r2' :
                    lblvar = fitness.r2( self.W, '_dataframe', column1, column2)
                    self.W.pop_indentlevel()
                    w( 1, 'graphlabels["%s"] = "R2 = %%0.2f" %% ( %s)' % ( column, lblvar))
                elif lblfunc == 'rmse' :
                    lblvar = fitness.rmse( self.W, '_dataframe', column1, column2)
                    self.W.pop_indentlevel()
                    w( 1, 'graphlabels["%s"] = "RMSE = %%0.2f" %% ( %s)' % ( column, lblvar))
                else :
                    self.W.set_error()
                #self.W.pop_indentlevel()
                #w( 1, 'graphlabels["%s"] = "NSE = %%0.2f" %% ( %s)' % ( column, lblvar))
## prototype END

    smoothen = _graph.get_property( 'interpolate', False)
    if smoothen :
        w( 1, 'from scipy import interpolate')

    xcolumn = '_dataframe.index'
    parametric_plot = self._find_columns( ['x-axis'], columns)
    parametric = len(parametric_plot) > 0
    if parametric :
        xcolumn = '_dataframe["%s"]' % ( parametric_plot[0])
        ## delete x-axis column from column list
        columns.remove( parametric_plot[0])
    else :
        if smoothen :
            xcolumn = '_dataframe["row"]'


    w( 1, 'columns = [ %s]' % ( ','.join([ '"%s"' % c for c in columns])))
    w( 1, 'for j, column in enumerate( columns) :')
    ycolumn = '_dataframe[column]'
## NOTE this seems not to be necessary
##    if parametric :
##        w( 2, 'xy = pandas.concat( [ %s.dropna(), %s.dropna()], axis=1, join="inner")' % ( xcolumn, ycolumn))
##        w( 2, 'print xy')
##        xcolumn = 'xy["%s"]' % ( parametric_plot[0])
##        ycolumn = 'xy[column]'
    if smoothen :
        w( 2, 'tck, u = interpolate.splprep( [ %s, %s], s=1)' % ( xcolumn, ycolumn))
        w( 2, 'u_new = numpy.arange( 0.0, 1.0, 0.0001)')
        w( 2, 'data = interpolate.splev( u_new, tck)')
        xcolumn = 'data[0]'
        ycolumn = 'data[1]'


    color = ''
    if _graph.get_property( "colormap") and not _graph.get_property( "color") :
        w( 2, 'col = %f + ( %f - %f) * float( j)/float( len( columns))' % ( c_lo, c_hi, c_lo))
        color = ', color=matplotlib_colormap.%s( col)' % ( _graph.get_property( "colormap"))
    w( 2, '_axes.plot( %s, %s %s %s, label=graphlabels[column], gid="%%s" %% ( column))' \
        % ( xcolumn, ycolumn, color, self._make_args( 'l', \
                zorder=_graph.zorder, \
                color=_graph.get_property( 'color'), \
                linestyle=self._get_linestyle( _graph.get_property( 'linestyle', 'solid')), \
                linewidth=_graph.get_property( 'linewidth'), \
                marker=_graph.get_property( 'marker'), \
                markersize=_graph.get_property( 'markersize'), \
                markeredgecolor=_graph.get_property( 'markeredgecolor'), \
                markeredgewidth=_graph.get_property( 'markeredgewidth'), \
                markerfacecolor=_graph.get_property( 'markercolor'), \
                markevery=_graph.get_property( 'markerstride') \
        )))
                #visible=self._toggle( _graph.get_property( 'hidden', False))

    return method_call

