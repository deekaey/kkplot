
##  helpers shared by the matplotlib engine and its plot methods

import ast
import warnings

from kkplot.kkutils.log import *

def lit( _value) :
    """Strings from the plot file used to be pasted into generated code as
    "..." literals, so backslash escapes (e.g. '\\\\frac' -> '\\frac') were
    interpreted by Python. Keep that behaviour."""
    if not isinstance( _value, str) or '\\' not in _value :
        return _value
    try :
        with warnings.catch_warnings() :
            warnings.simplefilter( 'ignore')
            return ast.literal_eval( '"%s"' % ( _value))
    except ( SyntaxError, ValueError) :
        return _value

def kwargs( **_kwargs) :
    """keyword arguments with unset (None) values dropped"""
    return { k: lit( v) for k, v in _kwargs.items() if v is not None }

def linestyle( _linestyle) :
    if _linestyle in ( 'solid', 'line', 'lines') :
        return '-'
    elif _linestyle in ( 'point', 'points') :
        return 'None'
    elif _linestyle == 'dashdot' :
        return '-.'
    elif _linestyle in ( 'dashed', 'dash', 'dashes') :
        return '--'
    elif _linestyle == 'dotted' :
        return ':'
    kklog_warn( 'unsupported line style "%s"' % _linestyle)
    return '-'

def colormap( _name) :
    import matplotlib.cm
    return getattr( matplotlib.cm, _name)

def find_columns( _subcolumns, _columns) :
    return [ column for subcolumn in _subcolumns for column in _columns \
        if column.endswith( '.%s' % ( subcolumn)) ]

def column_label( _graph, _column) :
    label = _graph.get_property( 'label.%s' % ( _column))
    return lit( '_nolabel' if label is None else '%s' % ( label))

def column_labels( _graph, _columns) :
    return { c: column_label( _graph, c) for c in _columns }

def line_kwargs( _graph, **_overrides) :
    """common Line2D options of line-like graphs"""
    kw = dict(
        zorder=_graph.zorder,
        color=_graph.get_property( 'color'),
        linestyle=linestyle( _graph.get_property( 'linestyle', 'solid')),
        linewidth=_graph.get_property( 'linewidth'),
        marker=_graph.get_property( 'marker'),
        markersize=_graph.get_property( 'markersize'),
        markeredgecolor=_graph.get_property( 'markeredgecolor'),
        markeredgewidth=_graph.get_property( 'markeredgewidth'),
        markerfacecolor=_graph.get_property( 'markercolor'),
        markevery=_graph.get_property( 'markerstride'))
    kw.update( _overrides)
    return kwargs( **kw)

def colorbar( _axes, _mappable, _label, **_kwargs) :
    return _axes.get_figure().colorbar( _mappable, ax=_axes, label=lit( _label), **kwargs( **_kwargs))

def fixed( _value, _fmt='%f') :
    """value as it came out of the formerly generated code"""
    return float( _fmt % ( _value))

class timedelta( object) :
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

class timeperiod( timedelta) :
    @property
    def seconds( self) :
        return super().seconds + 1.0
    @property
    def minutes( self) :
        return super().minutes + 1.0
    @property
    def hours( self) :
        return super().hours + 1.0
    @property
    def days( self) :
        return super().days + 1.0

def sort_by_zorder( _handles, _labels) :
    z_h = [ handle.get_zorder() if hasattr( handle, 'get_zorder') else 0 for handle in _handles ]
    z_H = [ 0] * len( _handles)
    for k1, z1 in enumerate( z_h) :
        for k2, z2 in enumerate( z_h) :
            if k1 != k2 and ( z1 > z2 or ( z1 == z2 and k2 > k1)) :
                z_H[k2] += 1

    new_handles = [ None] * len( _handles)
    new_labels = [ ''] * len( _handles)
    for k, ( handle, label) in enumerate( zip( _handles, _labels)) :
        new_handles[z_H[k]], new_labels[z_H[k]] = handle, label
    return new_handles, new_labels

def trapezoid( *_args, **_kwargs) :
    from scipy import integrate
    trapz = getattr( integrate, 'trapezoid', None) or integrate.trapz
    return trapz( *_args, **_kwargs)
