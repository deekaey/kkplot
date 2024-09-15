
def kkplot_pythonmatplotlib_time_regressionpoint( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    dataframe = _kwargs['dataframe']
    method_call = 'kkplot_plot_time_regressionpoint_%s( "%s", _dataframe=%s, _axes=%s)' \
        % ( self._canonicalize_name( _id), _id, dataframe, axes)
    auxialiary_columns = [ cols[0] for cols in _auxialiary_columns]

    w = self.W.iappendnl
    w( 0, 'import scipy')
    w( 0, 'import scipy.integrate as scipy_integrate')
    w( 0, 'scipy_version = scipy.__version__')
    w( 0, 'def kkplot_plot_time_regressionpoint_%s( _id, _dataframe, _axes) :' % ( self._canonicalize_name( _id)))
    w( 1, '_axes.set_gid( _id)')
    timeresolution = _graph.get_property( "timeresolution", "day")
    w( 1, 'time_period = %f ## resolution is %s' % ( _graph.domain.time_period( timeresolution), timeresolution))

    w( 1, 'data_column_x = "%s"' % ( _columns[0]))
    w( 1, '## integrate')

    w( 1, 'data_column_y = "%s"' % ( auxialiary_columns[0]))
    w( 1, '## integrate')

## timeseries "A"
    if _graph.get_property( 'setop', 'union') == 'union' :
        w( 1, 'data_x = _dataframe[data_column_x].loc[_dataframe[data_column_x].notnull()]')
        w( 1, 'nodes_x = numpy.array([0]+[kkplot_matplotlib_timedelta( data_x.index[i+1]-data_x.index[i]).%ss for i,t in enumerate( data_x.index[:-1])]).cumsum()' % ( timeresolution))
    elif _graph.get_property( 'setop') == 'intersect' :
        if _graph.get_property( 'op', 'integrate') == 'integrate' :
            w( 1, 'data_x = _dataframe[data_column_x].copy()')
            w( 1, 'data_x.loc[ _dataframe[data_column_x].isnull()|_dataframe[data_column_y].isnull()] = 0.0')
            w( 1, 'nodes_x = _dataframe.index')
        elif (_graph.get_property( 'op') == 'mean') or  (_graph.get_property( 'op') == 'max') :
            w( 1, 'data_x = _dataframe[data_column_x].loc[_dataframe[data_column_x].notnull()&_dataframe[data_column_y].notnull()]')
        else :
            pass

    if _graph.get_property( 'op', 'integrate') == 'integrate' :
        w( 1, 'if scipy_version >= "1.13.0":')
        w( 2, 'point_x = scipy_integrate.trapezoid( data_x, x=nodes_x)')
        w( 1, 'else:')
        w( 2, 'point_x = scipy_integrate.trapz( data_x, x=nodes_x)')
        w( 1, 'point_x = point_x / kkplot_matplotlib_timeperiod( data_x.index[-1]-data_x.index[0]).%ss * time_period' % ( timeresolution))
    elif _graph.get_property( 'op') == 'mean' :
        w( 1, 'point_x = data_x.mean()')
    elif _graph.get_property( 'op') == 'max' :
        w( 1, 'point_x = data_x.max()')
    else :
        w( 1, 'point_x = data_x')
        pass

## timeseries "B"
    if _graph.get_property( 'setop', 'union') == 'union' :
        w( 1, 'data_y = _dataframe[data_column_y].loc[_dataframe[data_column_y].notnull()]')
        w( 1, 'nodes_y = numpy.array([0]+[kkplot_matplotlib_timedelta( data_y.index[i+1]-data_y.index[i]).%ss for i,t in enumerate( data_y.index[:-1])]).cumsum()' % ( timeresolution))
    elif _graph.get_property( 'setop') == 'intersect' :
        if _graph.get_property( 'op', 'integrate') == 'integrate' :
            w( 1, 'data_y = _dataframe[data_column_y].copy()')
            w( 1, 'data_y.loc[ _dataframe[data_column_x].isnull()|_dataframe[data_column_y].isnull()] = 0.0')
            w( 1, 'nodes_y = _dataframe.index')
        elif (_graph.get_property( 'op') == 'mean') or  (_graph.get_property( 'op') == 'max') :
            w( 1, 'data_y = _dataframe[data_column_y].loc[_dataframe[data_column_x].notnull()&_dataframe[data_column_y].notnull()]')
        else :
            pass

    if _graph.get_property( 'op', 'integrate') == 'integrate' :
        w( 1, 'if scipy_version >= "1.13.0":')
        w( 2, 'point_y = scipy_integrate.trapezoid( data_y, x=nodes_y)')
        w( 1, 'else:')
        w( 2, 'point_y = scipy_integrate.trapz( data_y, x=nodes_y)')
        w( 1, 'point_y = point_y / kkplot_matplotlib_timeperiod( data_y.index[-1]-data_y.index[0]).%ss * time_period' % ( timeresolution))
    elif _graph.get_property( 'op') == 'mean' :
        w( 1, 'point_y = data_y.mean()')
    elif _graph.get_property( 'op') == 'max' :
        w( 1, 'point_y = data_y.max()')        
    else :
        w( 1, 'point_y = data_y')
        pass


    w( 0, '')
    w( 1, 'label = %s' % ( self._stringify( _graph.label( _columns[0]))))
    graphargs_common = self._make_args( 'l', \
                zorder=_graph.zorder, \
                marker=_graph.get_property( "marker", "o"), \
                markersize=_graph.get_property( "markersize"), \
                markeredgecolor=_graph.get_property( "markeredgecolor"), \
                markeredgewidth=_graph.get_property( "markeredgewidth"), \
                markerfacecolor=_graph.get_property( "markercolor"))

    if _graph.get_property( 'op') == 'all' :
        w( 1, 'concat = pandas.concat( [ _dataframe[c].dropna() for c in _dataframe.columns], axis=1, join="inner")')
        w( 1, '_axes.plot( concat[data_column_x], concat[data_column_y] %s %s, label="%%s" %% ( label), gid="%%s" %% ( data_column_x))' \
            % ( graphargs_common, self._make_args( 'l', \
                    color=_graph.get_property( "color"), \
                    linewidth=0.0 \
            )))
        w( 1, 'return [( concat[data_column_x],  concat[data_column_y])]')
        return method_call

    elif _graph.get_property( "xerror") is None and _graph.get_property( "yerror") is None :
        w( 1, '_axes.plot( point_x, point_y %s %s, label="_%%s" %% ( label), gid="%%s" %% ( data_column_x))' \
            % ( graphargs_common, self._make_args( 'l', \
                    color=_graph.get_property( "color"), \
                    linewidth=_graph.get_property( "linewidth") \
            )))
    else :
        w( 1, '_axes.errorbar( point_x, point_y, fmt="" %s %s)' \
            % ( graphargs_common, self._make_args( 'l', \
                    xerr=_graph.get_property( "xerror"), \
                    yerr=_graph.get_property( "yerror"), \
                    capsize=_graph.get_property( "capsize"), \
                    ecolor=_graph.get_property( "color"), \
                    elinewidth=_graph.get_property( "linewidth") \
            )))

    if False: #_graph.label( _columns[0]) :
        self.W.iappend  ( 1, 'label_orientation= "%s"\n' % _graph.get_property( "labelorientation", "right"))
        self.W.iappend  ( 1, '_axes.annotate( ')
        self.W.append   (    'label, xy=(point_x, point_y), xytext=( -10, 10), textcoords="offset points", ha=label_orientation, va="bottom", ')
        self.W.append   (    'bbox=dict( boxstyle="round,pad=0.2", lw=1.0, ec="black", fc="yellow", alpha=0.2), ')
        self.W.append   (    'arrowprops=dict( lw=0.5, ec="black", facecolor="black", arrowstyle="-|>,head_length=0.2,head_width=0.1", connectionstyle="arc3,rad=-0.3")')
        self.W.appendnl (    ')')

    w( 1, 'return [( point_x, point_y)]')

    return method_call


