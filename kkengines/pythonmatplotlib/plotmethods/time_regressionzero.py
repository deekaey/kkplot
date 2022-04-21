
def kkplot_pythonmatplotlib_time_regressionzero( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    method_call = 'kkplot_plot_time_regressionzero_%s( "%s", _axes=%s, _graphresults=%s)' \
        % ( self._canonicalize_name( _id), _id, axes, _kwargs['graphresults'])
    columns = _columns
    for aux_columns in _auxialiary_columns :
        columns += aux_columns

    w = self.W.iappendnl
    w( 0, 'def kkplot_plot_time_regressionzero_%s( _id, _axes, _graphresults) :' \
        % ( self._canonicalize_name( _id)))
    w( 1, '_axes.set_gid( _id)')

    w( 1, 'graphid = "%s"' % ( _graph.graphid))
    w( 1, 'points_names = [ %s]' \
        % ( ','.join( [ ','.join( '"%s"' % ( dep) for dep in _graph.dependencies( column)) for column in columns if not _graph.is_graphresult( column)])))
    w( 1, 'x, y = list(), list()')
    w( 1, 'for points_name in points_names :')
    w( 2, 'for points in _graphresults[points_name] :')
    w( 3, 'try:')
    w( 3, '    dummy = iter(points[0])')
    w( 3, '    x.append( points[0].tolist())')
    w( 3, 'except:')
    w( 3, '    x.append( [points[0]])')
    w( 3, 'try:')
    w( 3, '    dummy = iter(points[1])')
    w( 3, '    y.append( points[1].tolist())')
    w( 3, 'except:')
    w( 3, '    y.append( [points[1]])')

    #flatten listst if points contain list
    w( 1, 'try :')
    w( 2, 'x = [a for b in x for a in b]')
    w( 2, 'y = [a for b in y for a in b]')
    w( 1, 'except :')
    w( 2, 'pass')
    w( 1, 'x, y = pandas.Series( x), pandas.Series( y)')
    w( 0, '')

    #w( 1, 'print "x=",x, "  y=",y')
    w( 1, 'import statsmodels.api as sm')
    w( 1, 'regression_model = sm.OLS(y, x).fit()')
    w( 1, '_axes.plot( x, regression_model.predict(x) %s, label="_%%s" %% ( graphid), gid="%%s" %% ( graphid))' \
        % ( self._make_args( 'l', \
                zorder=_graph.zorder, \
                linestyle=self._get_linestyle( _graph.get_property( 'linestyle', 'solid')), \
                linewidth=_graph.get_property( 'linewidth'), \
                color=_graph.get_property( "color") \
    )))
    w( 1, '_axes.plot( [0.0, 1000.0], [0.0, 1000.0], label="", gid="%s" % ( graphid), color="black", linestyle="dashed")')

    w( 1, 'f = regression_model.predict(x)')
    w( 1, 'm = "%.2f" % ((f.iloc[-1]-f.iloc[0]) / (x.iloc[-1]-x.iloc[0]))')
    coords = _graph.get_property( 'textcoordinates', [0.05, 0.92])
    w( 1, 'textcoordinates=[%f, %f]' %(coords[0], coords[1]))
    w( 1, 'name = "%s"' %("%s" %_graph.get_property( 'name', '')))
    w( 1, 'if name !="":')
    w( 2, 'name = name+": "')
    w( 1, '_axes.annotate( "%sb=%s (y=bx)" %(name,m), xy=(0.0,0.0), xycoords="axes fraction", xytext=(textcoordinates[0], textcoordinates[1]), textcoords="axes fraction")')
    w( 0, '')
    w( 1, 'return regression_model')

    return method_call

