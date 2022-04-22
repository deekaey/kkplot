
from kkplot.kkutils.log import *

class ident_t( object) :
    def __init__( self, _name) :
        self._name = _name
    def __str__( self) :
        return self._name

## http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.table
def kkplot_pythonmatplotlib_non_bartable( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_non_bartable_%s( "%s", _dataframe=%s, _axes=%s, _graphresults=%s)' \
        % ( self._canonicalize_name( _id), _id, dataframe, axes, _kwargs['graphresults'])

    columns = [ column for column in _columns if not column.endswith( 'below_')]
    aboverowids = [ column for column in _columns if column.endswith( 'below_')]
    aboverowid = None
    if len( aboverowids) > 1 :
        kklog_fatal( 'too many leading rows  [rows=%s]' % ( aboverowids))
    elif len( aboverowids) == 1 :
        aboverowid = aboverowids[0]
    else :
        pass

    appendtablerow = len( columns) != len( _columns)
    for auxcolumns in _auxialiary_columns :
        columns += auxcolumns

    w = self.W.iappendnl

    w( 0, 'def kkplot_plot_non_bartable_%s( _id, _dataframe, _axes, _graphresults) :' % ( self._canonicalize_name( _id)))
    w( 1, '_axes.set_gid( _id)')

    kklog_debug( 'dependencies=%s' % ( _graph.dependencies( columns[0])))

    #w( 1, 'appendtable = _graphresults.get( 'previousrow_
    #    % ( ','.join( [ ','.join( '"%s"' % ( dep) for dep in _graph.dependencies( column)) for column in columns if not _graph.is_graphresult( column)])))

    w( 1, 'for column in [%s] :' % ( ','.join([ '"%s"' % c for c in columns])))
    w( 2, 'print column, "=", _dataframe[column].values')

    if aboverowid is None :
        w( 1, 'rownb = 0')
    else :
        w( 1, 'res = _graphresults["%s"]' % ( _graph.dependencies( aboverowid)[0]))
        w( 1, 'rownb = res["row"] + 1')

    w( 1, 'N_rows = %s' % ( 'len( _dataframe)' if _graph.get_property( 'nrows', 0) < 1 else str( _graph.get_property( 'nrows'))))
    w( 1, 'n_rows = len( _dataframe)')
    w( 1, 'n_cols = %d' % ( len( columns)))

    w( 1, 'colors = matplotlib_colormap.%s( numpy.linspace( 0.2, 0.8, N_rows))' % ( _graph.get_property( 'colormap', 'PuBu')))

    w( 1, 'columns = [%s]' % ( ','.join([ '"%s"' % c for c in columns])))
    w( 1, 'barwidth = %f' % ( float( _graph.get_property( 'tablecolumnwidth', 1.0)) / 2.0))
    if aboverowid is None :
        w( 1, 'heightoffsets = numpy.zeros( n_cols)')
    else :
        w( 1, 'heightoffsets = res["heightoffsets"]')
    w( 1, 'W = %f' % ( float( _graph.get_property( 'xlimithigh', 0.0)) - float( _graph.get_property( 'xlimitlow', 1.0))))
    w( 1, 'W = float( n_cols) if W < 0.0 else W')
    w( 1, 'wx = W/n_cols')
    w( 1, 'left = numpy.array( range( n_cols)) + wx/2.0 - barwidth/2.0')
    w( 1, 'for row in xrange( n_rows) :')
    w( 2, 'values = numpy.array( _dataframe[columns].iloc[row,:].values)')

    w( 2, '_axes.bar( left=left, height=values, width=barwidth, bottom=heightoffsets, color=colors[rownb])')
    w( 2, 'heightoffsets = heightoffsets + values')

    w( 1, 'graphlabels = { %s }' % ( self._make_labels( columns, _graph)))
    w( 1, 'columnlabels = [ graphlabels[g] for g in columns ]')
    if aboverowid is None :
        w( 1, 'tbl = _axes.table( cellText=[[ ""]*n_cols] %s, colLabels=columnlabels, rowColours=[ colors[rownb]])' \
            % ( self._make_args( 'l', cellLoc=_graph.get_property( 'tabletextalign', 'center'), loc=_graph.get_property( 'tablealign', 'bottom'))))

        w( 1, 'for colnb, column in enumerate( columns) :')
        w( 2, 'headcell = tbl.get_celld()[(0, colnb)]')
        w( 2, 'headcell.set_text_props( verticalalignment="bottom")')
        w( 2, 'headcell.set_height( 2.5*headcell.get_height())')
        #w( 2, 'headcell.set_edgecolor( "none")')
    else :
        w( 1, 'tbl = res["table"]')

    rowlabels = _graph.get_property( 'ylabel', '')
    if rowlabels is None or isinstance( rowlabels, list) :
        pass
    else :
        rowlabels = [ rowlabels]
    w( 1, 'rowlabels = [ %s]' % ( ','.join([ '"%s"' % label for label in rowlabels])))

    w( 1, 'for row in xrange( n_rows) :')
    w( 2, 'for col, value in enumerate( _dataframe[columns].values[row,:]) :')
    w( 3, 'tbl.add_cell( N_rows-rownb+row, col, 1.0/float( n_cols), 0.2/N_rows, text="$%%.2f$" %% (value) %s)' \
        % ( self._make_args( 'l', loc=_graph.get_property( 'tabletextalign', 'center'), \
            edgecolor=_graph.get_property( 'edgecolor'), \
            facecolor='none' #facecolor=_graph.get_property( 'backgroundcolor', ident_t( 'colors[rownb]')))))
    )))

    ## ylabel cell
    w( 2, 'tbl.add_cell( N_rows-rownb+row, -1, %f*1.0/float( n_cols), 0.2/N_rows, text=rowlabels[row] %s)' \
        % ( _graph.get_property( 'xstretchlabelbox', 1.1), self._make_args( 'l', loc=_graph.get_property( 'tableylabelalign', 'right'), \
                edgecolor=_graph.get_property( 'ylabeledgecolor', 'none'), facecolor=_graph.get_property( 'backgroundcolor', ident_t( 'colors[rownb]')))))

    if _graph.get_property( 'tablerowheight') is None :
        self.W.comment_on()
    w( 1, 'for cell in tbl.get_celld().values() :')
    w( 2, 'cell.set_height( %f)' % ( float( _graph.get_property( 'tablerowheight', 1.0))))
    self.W.comment_off()
    if _graph.get_property( 'tablecolumnwidth') is None :
        self.W.comment_on()
    w( 1, 'for cell in tbl.get_celld().values() :')
    w( 2, 'cell.set_width( %f)' % ( float( _graph.get_property( 'tablecolumnwidth', 1.0))))
    self.W.comment_off()

    #w( 1, '#_axes.axis( "off")')
    w( 1, '_axes.set_xticks( [])')
    w( 1, '_axes.figure.subplots_adjust( left=0.21, bottom=0.21)')

    w( 1, 'tbl.auto_set_font_size( False)')
    w( 1, 'tbl.set_fontsize( %f)' % ( _graph.get_property( 'fontsize', 10)))

    w( 1, 'return dict( table=tbl, heightoffsets=heightoffsets, row=rownb)')

    return method_call


