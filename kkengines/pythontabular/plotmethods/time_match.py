
from kkutils.log import *

def kkplot_pythontabular_time_match( self, _id, _graph, _columns, _auxialiary_columns, **_kwargs) :
    w = self.writer.iappendnl

    graphid = self._canonicalize_name( _id)
    dataframe = _kwargs['dataframe']

    columns = _columns
    for auxialiary_columns in _auxialiary_columns :
        columns += auxialiary_columns

    w( 0, 'def kkplot_tabular_time_match_%s( _id, _dataframe) :' % ( graphid))
#    w( 1, 'headers = { %s }' % ( self._make_labels( columns, _graph)))
    w( 1, 'labels = %s' % _graph._labels)
    w( 1, 'rowlabel = "%s"' % _graph.get_property( 'rowlabel', None))
    w( 1, '_dataframe.index=[rowlabel for r in range(len(_dataframe))]')
    w( 1, 'columns = %s' % columns)
    w( 1, 'join = %s' %( _graph.get_property("join", None)))
    w( 1, 'if join : ')
    w( 2, 'concat = pandas.concat( [ _dataframe[c].dropna() for c in columns], axis=1, join="inner")')
    w( 1, 'else : ')
    w( 2, 'concat = pandas.concat( [ _dataframe[c].dropna() for c in columns], axis=1)')
    w( 1, 'out = []')
    w( 1, 'for index, row in concat.iterrows() :')
    w( 2, 'try:')
    w( 3, 'lab = rowlabel')
    w( 2, 'except:')
    w( 3, 'lab = index')
    w( 2, 'out.append( [lab] + row.tolist())')
    w( 1, 'return out' )

    method_call = 'kkplot_tabular_time_match_%s( "%s", _dataframe=%s)' \
         % ( graphid, _id, dataframe)
    return  method_call

