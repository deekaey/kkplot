
from kkutils.log import *

def kkplot_pythontabular_time_fit( self, _id, _graph, _columns, _auxialiary_columns, **_kwargs) :
    w = self.writer.iappendnl

    graphid = self._canonicalize_name( _id)
    dataframe = _kwargs['dataframe']

    columns = _columns
    for auxialiary_columns in _auxialiary_columns :
        columns += auxialiary_columns

    fitness_func = _graph.get_property( 'function', 'nse')

    w( 0, 'def kkplot_tabular_time_fit_%s( _id, _dataframe) :' % ( graphid))
#    w( 1, 'headers = { %s }' % ( self._make_labels( columns, _graph)))
    w( 1, 'rowlabel = "%s"' % _graph.get_property( 'rowlabel', None))
    fitness = kkplot_pythontabular_time_fitness( \
        self, _graph, columns, fitness_func, dataframe, _kwargs)
    if fitness is [] :
        return None

    w( 1, 'columns = [] ')
    for f in fitness:
        w( 1, 'columns.append( %s)' % f)
    w( 1, 'columns.insert(0, rowlabel)')
    w( 1, 'return columns')

    method_call = 'kkplot_tabular_time_fit_%s( "%s", _dataframe=%s)' \
         % ( graphid, _id, dataframe)
    return  method_call


from kkengines.pythoncode import fitness

def kkplot_pythontabular_time_fitness( self, _graph, _columns, _fitness_func, _dataframe, _kwargs) :

    observed_column = None
    for column in _columns :
        if 'observed' in column:#column.endswith( '.observed') :
            observed_column = column
    simulated_column = None
    for column in _columns :
        if 'simulated' in column:#column.endswith( '.simulated') :
            simulated_column = column

    fitnessvalue = []

    if type(_fitness_func) is not list:
        _fitness_func = [_fitness_func]

    for ff in _fitness_func:
        if ff == 'nse' or ff == 'nashsutcliffe' :
            self.writer.push_indentlevel()
            fitnessvalue.append( fitness.nse( self.writer, '_dataframe', observed_column, simulated_column))
            self.writer.pop_indentlevel()
        elif ff == 'r2' :
            self.writer.push_indentlevel()
            fitnessvalue.append( fitness.r2( self.writer, '_dataframe', observed_column, simulated_column))
            self.writer.pop_indentlevel()
        elif ff == 'rmse' :
            self.writer.push_indentlevel()
            fitnessvalue.append( fitness.rmse( self.writer, '_dataframe', observed_column, simulated_column))
            self.writer.pop_indentlevel()
        else :
            kklog_error( 'requested fitness function "%s" does not exist' % ( ff))

    ## fallback
    return fitnessvalue

