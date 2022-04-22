
def kkplot_pythonbokeh_time_regressionline( self, _id, _graph, _axes_index, _columns, _auxialiary_columns, **_kwargs) :
    axes = '%s["%s"]' % ( _kwargs['axes'], _axes_index)
    method_call = 'kkplot_plot_time_regressionline_%s( "%s", _plot=%s, _graphresults=%s)' \
        % ( self._canonicalize_name( _id), _id, axes, _kwargs['graphresults'])
    columns = _columns
    for aux_columns in _auxialiary_columns :
        columns += aux_columns

    self.W.iappendnl( 0, 'def kkplot_plot_time_regressionline_%s( _id, _plot, _graphresults) :' % ( self._canonicalize_name( _id)))
    #self.W.iappendnl( 1, '_axes.set_gid( _id)')

    self.W.iappendnl( 1, 'graphid = "%s"' % ( _graph.graphid))
    self.W.iappendnl( 1, 'points_names = [ %s]' \
        % ( ','.join( [ ','.join( '"%s"' % ( dep) for dep in _graph.dependencies( column)) for column in columns if not _graph.is_graphresult( column)])))
    self.W.iappendnl( 1, 'x, y = list(), list()')
    self.W.iappendnl( 1, 'for points_name in points_names :')
    self.W.iappendnl( 2, 'for points in _graphresults[points_name] :')
    self.W.iappendnl( 3, 'try:')
    self.W.iappendnl( 3, '    dummy = iter(points[0])')
    self.W.iappendnl( 3, '    x.append( points[0].tolist())')
    self.W.iappendnl( 3, 'except:')
    self.W.iappendnl( 3, '    x.append( [points[0]])')
    self.W.iappendnl( 3, 'try:')
    self.W.iappendnl( 3, '    dummy = iter(points[1])')
    self.W.iappendnl( 3, '    y.append( points[1].tolist())')
    self.W.iappendnl( 3, 'except:')
    self.W.iappendnl( 3, '    y.append( [points[1]])')

    #flatten listst if points contain list
    self.W.iappendnl( 1, 'try :')
    self.W.iappendnl( 2, 'x = [a for b in x for a in b]')
    self.W.iappendnl( 2, 'y = [a for b in y for a in b]')
    self.W.iappendnl( 1, 'except :')
    self.W.iappendnl( 2, 'pass')    
    self.W.iappendnl( 1, 'x, y = pandas.Series( x), pandas.Series( y)')
    self.W.iappendnl( 0, '')

    #self.W.iappendnl( 1, 'print "x=",x, "  y=",y')
    self.W.iappendnl( 1, 'import statsmodels.api as sm')
    self.W.iappendnl( 1, 'xc = sm.add_constant(x)')
    self.W.iappendnl( 1, 'regression_model = sm.OLS(y, xc).fit()')
    coords = _graph.get_property( 'textcoordinates', [0.05, 0.92])
    self.W.iappendnl( 1, 'textcoordinates=[%f, %f]' %(coords[0], coords[1]))    
    self.W.iappendnl( 1, 'x_coord=textcoordinates[0]*_plot.plot_width')    
    self.W.iappendnl( 1, 'y_coord=textcoordinates[1]*_plot.plot_height')    
    self.W.iappendnl( 1, '_plot.line([-2*x.min(),2*x.max()],[-2*x.min(),2*x.max()], color="grey", line_dash="dashed")')    
    self.W.iappendnl( 1, '_plot.line( xc.iloc[:,1], regression_model.fittedvalues %s)' \
                       % ( self._make_args( 'l', \
                                       line_width=_graph.get_property( 'linewidth'), \
                                       color=_graph.get_property( "color") \
                           )))            
    #self.W.iappendnl( 1, '_axes.plot( [0.0, 1000.0], [0.0, 1000.0], label="", gid="%s" % ( graphid), color="grey") ')
    self.W.iappendnl( 1, 'f = regression_model.fittedvalues')
    self.W.iappendnl( 1, 'name = "%s"' %("%s" %_graph.get_property( 'name', '')))
    self.W.iappendnl( 1, 'plot_label = Label( x_units="screen", y_units="screen", x=x_coord, y=y_coord, text="R2: %.2f %s\\ny=%.1f+%.1fx" % (regression_model.rsquared, name, regression_model.params["const"], regression_model.params[0]))')
    self.W.iappendnl( 1, '_plot.add_layout( plot_label)')
    self.W.iappendnl( 0, '')
    self.W.iappendnl( 1, 'return regression_model')

    return method_call

