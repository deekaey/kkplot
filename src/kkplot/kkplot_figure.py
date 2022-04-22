
from kkplot.kkutils.log import *
from kkplot.kkutils.expand import *

import kkplot.kkplot_domains as kkplot_domains

import sys

GROUPBYTAG = '.SELECT_'
NSSEP = '.'  ## namespace separator
DSSEP = '@'  ## entity/datasource separator
NODEPMARKER = '_'
GRAPHRESULT = 'result'
GRAPHRESULTINTL = '%s%s' % ( GRAPHRESULT, NODEPMARKER)

KKCONSTS = dict( PI=3.141592653589793, E=2.718281828459045, K0=273.15, MC=12.0, MN=14.0, MO=16.0, MCH4=16.0, MCO2=44.0, CCDM=0.45)
KKFUNCS = dict( sin='numpy.sin', cos='numpy.cos', timeperiod='timeperiod', timestamp='timestamp',
    daysum='daysum', weeksum='weeksum', monthsum='monthsum', yearsum='yearsum',
    daymean='daymean', daymax='daymax', weekmean='weekmean', monthmean='monthmean', yearmean='yearmean',
    daystd='daystd', weekstd='weekstd', monthstd='monthstd', yearstd='yearstd',
    cumsum='cumsum', nansum='nansum', nanmean='nanmean', nanstd='nanstd',diff='diff', integral='integral', nanmin='nanmin',kkround='kkround')
    
def isreference( _dependency) :
    return  _dependency.startswith( NSSEP)
def asname( _dependency) :
    dssep_pos = _dependency.find( DSSEP)
    if dssep_pos == -1 :
        return _dependency
    return _dependency[:dssep_pos]
def nocolumndepends( _name) :
    return _name.endswith( NODEPMARKER)

class kkplot_namedconstants( object) :
    def __init__( self, _iniconsts) :
        self._namedconstants = dict()
        self._namedconstants.update( _iniconsts)

    @property
    def namedconstants( self) :
        return self._namedconstants
    def value( self, _namedconstant, _default=None) :
        return self._namedconstants.get( _namedconstant, _default)

    def add_constant( self, _namedconstant, _value) :
        self._namedconstants[_namedconstant] = _value
    def add_constants( self, _namedconstants) :
        self._namedconstants.update( _namedconstants)

class kkplot_namedfunctions( object) :
    def __init__( self, _inifuncs) :
        self._functions = dict()
        self._functions.update( _inifuncs)

    @property
    def functions( self) :
        return self._functions
    def name( self, _function, _default=None) :
        return self._functions.get( _function, _default)


## global named constants dictionary
kkplot_defines = kkplot_namedconstants( KKCONSTS)
## global named functions dictionary
kkplot_functions = kkplot_namedfunctions( KKFUNCS)

class kkplot_datasource( object) :
    def __init__( self, _name=None, _path=None, _format='table', _kind='table', _flavor='iso8601', _provider=None) :
        self._name = _name
        self.set_path( _path)

        ## location: data file, measurement file, ..
        self.kind = _kind
        ## data encoding: table, sqlite3, ..
        self.format = _format
        self._formatargs = dict()
        ## predefined data layouts: ldndc, ..
        self.flavor = _flavor
        self._flavorargs = dict()
        ## external program that produces the data stream
        self.provider = _provider

    @property
    def name( self) :
        return  self._name
    @property
    def path( self) :
        return  self._path
    @property
    def has_provider( self) :
        return self.provider != None

    @property
    def flavorargs( self) :
        return self._flavorargs
    def flavorarg( self, _arg, _default=None) :
        return self._flavorargs.get( _arg, _default)
    def add_flavorargs( self, _args) :
        if _args :
            self._flavorargs.update( _args)
    @property
    def formatargs( self) :
        return self._formatargs
    def formatarg( self, _arg, _default=None) :
        return self._formatargs.get( _arg, _default)
    def add_formatargs( self, _args) :
        if _args :
            self._formatargs.update( _args)

    def set_path( self, _path, _basepath=None) :
        import os
        self._path = None
        if _path is not None :
            self._path = _path.replace( '\\', '/')
            self._path = self._path.strip()

        if self._path is not None :
            self._path = kkexpand( self._path)
            if _basepath is not None and not os.path.isabs( self._path) :
                self._path = '%s/%s' % (  kkexpand( _basepath), self._path)
        return self._path

    def __str__( self) :
        return  'name=%s; path=%s; kind=%s; format=%s %s; flavor=%s %s; provider=%s' \
            % ( self._name, self._path, self.kind, self.format, self.formatargs, self.flavor, self.flavorargs, self.provider)

class kkterm( object) :
    def __init__( self, _position, _literal) :
        self.pos = _position
        self.literal = _literal
    def __repr__( self) :
        return '%s@%s' % ( self.literal, self.pos)

class kkplot_expr( object) :
    def __init__( self, _ns, _expr) :
        self._ns = _ns
        self._expr = _expr

    def get_lefthandside( self, _n) :
        lhs = self._get_lefthandside( self._expr)
        if lhs == '' or lhs is None :
            lhs = None
        elif lhs == '.' :
            lhs = '.%s%04d%s' % ( NODEPMARKER, _n, NODEPMARKER)
## sk:??        elif lhs.endswith( GRAPHRESULT) :
## sk:??            lhs = lhs.replace( GRAPHRESULT, GRAPHRESULTINTL)
        return lhs

    def _get_lefthandside( self, _expression) :
        expression = _expression
        if expression is not None :
            expressions = [ expr.strip() for expr in expression.split( '=')]
            if len( expressions) == 0 or len( expressions) > 2 :
                kklog_error( 'invalid expression  [expression="%s"]' % ( expression))
                raise RuntimeError( 'invalid expression')
            elif len( expressions) == 1 :
                expression = expressions[0]
            elif len( expressions) == 2 :
                expression = expressions[0].split( NSSEP).pop().strip()
                expression = '%s%s' % ( NSSEP, expression)
            else :
                assert( False)
        #kklog_debug( '_get_lefthandside(): expr="%s"' % ( expression))
        return expression

    def get_righthandside( self) :
        rhs = self._get_righthandside( self._expr)
        if rhs and rhs.endswith( GRAPHRESULT) :
            rhs = rhs.replace( GRAPHRESULT, GRAPHRESULTINTL)
        return rhs

    def _get_righthandside( self, _expression) :
        expression = _expression
        if expression is not None :
            expressions = [ expr.strip() for expr in expression.split( '=')]
            if len( expressions) == 0 or len( expressions) > 2 :
                kklog_error( 'invalid expression  [expression="%s"]' % ( expression))
                raise RuntimeError( 'invalid expression')
            elif len( expressions) == 1 :
                expression = None
            elif len( expressions) == 2 :
                expression = self._resolve_defines( expressions[1])
                #kklog_debug( 'rhs=%s' % ( expression))
            else :
                assert( False)
        return expression

    ## identifier contains  '[a-zA-Z][a-zA-Z0-9_.]*'
    ## constant expression  '[0-9]*[.][0-9]*'
    ## function calls  '[a-zA-Z][a-zA-Z0-9]*( <expr>)'
    def get_dependencies( self, _expression) :
        dependencies = self._get_identifiers( _expression)
        dependencies = sorted( set( dependencies))
        return dependencies

    def _get_identifiers( self, _expression) :
        identifiers = self._scan_expression( _expression)["I"]
        return identifiers

    ## simple scanner that extracts identifiers,
    ## functions and named constants
    ## NOTE  lacks support for
    ##  - scientific numbers, e.g., 1.0e-1
    ##  - test for well-formed expression
    def _scan_expression( self, _expression) :
        digits = '0123456789'
        identifierchars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_' + digits + NSSEP + DSSEP
        identifiernonheadchars = digits + DSSEP
        operatorchars = '+-*/%'
        identifiers = list()
        functions = list()
        namedconstants = list()
        numbers = list()
        tokens = list()

        token = ''
        number = ''
        expression = '%s%s' % ( _expression, '$') ## add stop marker
        for ( p, c) in enumerate( expression) :
            if token == '' and ( c in digits or ( number != '' and ( c == '.' or c == 'e' or c == 'E'))) :
                number += c
            elif c in identifierchars :
                if token == '' :
                    identpos = p
                token += c
            elif c == '(' and token != '' :
                functions.append( token) #kkterm( p, token))
                tokens.append( token)
                token = ''
            else :
                if token != '' and token != NSSEP :
                    if token[0] in identifiernonheadchars :
                        kklog_fatal( 'invalid identifier')
                        raise RuntimeError( 'invalid identifier')
                    if self._isnamedconst( token) :
                        namedconstants.append( token) #kkterm( p, token))
                        tokens.append( token)
                    else :
                        identifiers.append( token)
                        tokens.append( token)
                    token = ''
                elif number != '' :
                    numbers.append( number)
                    tokens.append( number)
                    number = ''
                if c in operatorchars and token != '$' :
                    tokens.append( c)
            if c in '(),' :
                tokens.append( c)

        kklog_debug( 'tokens:%s, functions:%s, identifiers:%s, namedconstants:%s' % ( tokens, functions, identifiers, str(namedconstants)))
        return  dict( I=identifiers, F=functions, D=namedconstants, T=tokens)

    def _resolve_defines( self, _expression) :
        expr = self._scan_expression( _expression)
        tokens = expr["T"]
        namedconstants = expr["D"]
        functions = expr["F"]

        expression = ""
        for token in tokens :
            tokenreplace = token
            if token in namedconstants :
                if not self._isnamedconst( token) :
                    kklog_fatal( 'named constant not defined  [token=%s]' % ( token))
                tokenreplace = '(%s)' % ( str( self._getconst( token)))
            elif token in functions :
                if not self._isfunc( token) :
                    kklog_fatal( 'function not defined  [token=%s]' % ( token))
                tokenreplace = str( self._getfunc( token))
            else :
                tokenreplace = kkexpand( "$"+token).replace('$','')
            expression += tokenreplace
        return expression

    def _isnamedconst( self, _token) :
        return _token in kkplot_defines.namedconstants
    def _getconst( self, _token) :
        return kkplot_defines.value( _token)
    def _isfunc( self, _token) :
        return _token in kkplot_functions.functions
    def _getfunc( self, _token) :
        return kkplot_functions.name( _token)


class kkplot_expressions( object) :
    def __init__( self, _namespace, _expressions) :
        self._ns = _namespace

        if _expressions is None :
            expressions = [ self._ns]
        elif type( _expressions) is list :
            if len( _expressions) == 0 :
                expressions = [ self._ns]
            else :
                expressions = _expressions
        else :
            ## assume string
            expressions = [ _expressions]

        self._names = list()
        rewrite_expressions = [ None] * len( expressions)
        for n, expression in enumerate( expressions) :
            name, rewrite_expression = self._parse_name( n, expression)
            if rewrite_expression is not None :
                rewrite_expressions[n] = rewrite_expression
            else :
                rewrite_expressions[n] = expressions[n]
            self._names.append( name)

        expressions = rewrite_expressions

        self._exprs = dict()
        self._deps = dict()
        if self.name is not None :
            collect_dependencies = list()
            for n, name in enumerate( self._names) :
                self._exprs[name], self._deps[name] = \
                    self._parse_expression( expressions[n])
                resolved_dependencies = list()
                for dependency in self._deps[name] :
                    resolved_dependency = self._resolveid( dependency)
                    self._exprs[name] = self._exprs[name].replace( \
                        dependency, resolved_dependency)
                    resolved_dependencies.append( resolved_dependency)
                self._deps[name] = resolved_dependencies

            ## inject "graphresult" entity
            graphresult_name = '%s%s%s%s' % ( NSSEP, self._ns, NSSEP, GRAPHRESULTINTL)
            self._exprs[graphresult_name] = '0'
            self._deps[graphresult_name] = list()
            for name in self._names :
                self._deps[graphresult_name].append( name)
            self._names.append( graphresult_name)
            #kklog_debug( '[%s] expr=%s; deps=%s' % ( self._ns, self._exprs, self._deps))

    def _parse_name( self, _n, _expression) :
        if _expression is None :
            return self._resolveid( '%s%s' % ( NSSEP, self._ns)), self._ns
        elif _expression == ':none:' :
            kklog_debug( 'phony graph  [graph=%s]' % ( self._ns))
            return None, None

        expr = kkplot_expr( self._ns, _expression)
        lhs = expr.get_lefthandside( _n)
        rhs = None
        if lhs is not None :
            rhs = expr.get_righthandside()
            if rhs is None :
                rhs = '%s%s=%s' % ( NSSEP, asname( lhs), lhs)
                lhs = '%s%s' % ( NSSEP, asname( lhs))
            else :
                rhs = None
            lhs = self._resolveid( lhs)
        return lhs, rhs

    def _parse_expression( self, _expression) :
        rhs, dependencies = None, list()
        if _expression is None :
            pass
        else :
            expr = kkplot_expr( self._ns, _expression)
            rhs = expr.get_righthandside()
            if rhs is not None :
                dependencies = expr.get_dependencies( rhs)
        #kklog_debug( 'expr=%s  ->  rhs=%s;  deps=%s' % ( _expression, rhs, dependencies))

        return ( rhs, dependencies)

    def _resolveid( self, _id, _ns=None) :
        if _ns == None :
            _ns = self._ns
        if _id is None :
            return None

        _id = _id.strip()
        if  isreference( _id[0]) :
            _id = _id.strip( NSSEP).strip()
        else :
            return _id

        ns_s = _ns.split( NSSEP)
        id_s = _id.split( NSSEP)

        if len( id_s) == 0 or len( id_s) > 3 :
            kklog_fatal( 'namespace is messed up')
        elif len( id_s) == 1 :
            return '%s%s%s%s%s%s' % ( NSSEP, ns_s[0], NSSEP, ns_s[1], NSSEP, _id)
        elif len( id_s) == 2 :
            return '%s%s%s%s' % ( NSSEP, ns_s[0], NSSEP, _id)
        elif len( id_s) == 3 :
            return '%s%s' % ( NSSEP, _id)
        else :
            pass
        kklog_fatal( 'wow, how are you doing it :o ?!')


    @property
    def name( self) :
        return self._names[0]
    @property
    def names( self) :
        return self._names
    def dependencies( self, _name) :
        return self._deps[_name]
    def expression( self, _name) :
        return self._exprs[_name]

    @property
    def terminals( self) :
        terms = list()
        for name in self.names :
            terms += [ '%s' % term for term in self._deps[name] if not isreference( term)]
        return terms

    def __str__( self) :
        return ';'.join([ '(%s, %s, %s)' % ( n, self._exprs[e], self._deps[d]) for ( n, e, d) in zip( self._names, self._exprs, self._deps)])


import itertools
class kkplot_graph( object) :
    def __init__( self, _id, _names, _labels, _namespace) :
        self._ns = _id
        if _namespace is not None :
            self._ns = '%s%s%s' % ( _namespace, NSSEP, _id)

        self._id = self._ns
        self._exprs = kkplot_expressions( self._ns, _names)

        self._labels = _labels
        if self._labels is None :
            self._labels = [ self._id] if self.name is None else self.names
        elif self._labels == ':none:' :
            kklog_debug( 'no label  [graph=%s]' % self._id)
            self._labels = [ None]
        elif type( _labels) is not list :
            self._labels = [ _labels]

        if len( self._labels) > len( self.names) :
            kklog_warn( 'too many labels, dropping unused ones  [graph=%s]' % ( self._id))
            self._labels = self._labels[:len(self.names)]
        elif len( self._labels) < len( self.names) :
## sk:off            if type( _labels) is list :
## sk:off                kklog_warn( 'not enough labels, filling with None  [graph=%s]' % ( self._id))
            self._labels += [ None] * ( len( self.names) - len( self._labels))
        else :
            pass

        self._domain = None

        self._groups = list()
        self._datasources = dict()
        self._properties = dict()

    def add_group( self, _group_name, _datacol) :
        datacol = []
        for elem in _datacol :
            if type( elem) is list :
                if len( elem) == 0 :
                    kklog_warn( 'empty sequence  [group=%s]' % ( _group_name))
                    return
                value_type = type( elem[0])
                if value_type is int :
                    if len( elem) == 1 :
                        datacol += range( elem[0], elem[0]+1)
                    elif len( elem) == 2 :
                        datacol += range( elem[0], elem[1]+1)
                    elif len( elem) == 3 :
                        if elem[2] == 0 :
                            kklog_error( 'step size is 0 for sequence [group=%s,seq=%s]' % ( _group_name, elem))
                            return
                        sgn = lambda i : -1 if i < 0 else 1
                        datacol += range( elem[0], elem[1]+sgn(elem[2]), elem[2])
                    else :
                        kklog_warn( 'sequence not understood  [group=%s,seq=%s]' % ( _group_name, elem))
                        return
                if value_type is str :
                    datacol += elem
            else :
                datacol += [ elem]
        self._groups.append( ( _group_name, datacol))

    def groups( self) :
        return [ group[0] for group in self._groups ]
    def groupname( self, _index) :
        return self._groups[_index][0]
    def groupsize( self, _group_name) :
        for k, group in enumerate( self._groups) :
            if group[0] == _group_name :
                return len( group[1])
        return 0
    def asindex( self, _select) :
        return  '%s' % ( '_'.join( [ str( self._groups[k][1].index(c)) for k, c in enumerate( _select)]))
    def dataid( self, _select, _id) :
        this_id = asname( _id)
        datasource = self.get_datasource( _id, _warn=False)
        if datasource :
            this_id = '%s%s' % ( DSSEP, NSSEP.join([ datasource.name, self._ns, this_id]))
        if _select is None or _select == () :
            return  this_id
        return  '%s%s%s' % ( this_id, GROUPBYTAG, self.asindex( _select))
    def dataids( self, _select=None) :
        return [ self.dataid( _select, asname( n_id)) for n_id in self.terminals]
    def referenceid( self, _select=None, _id=None) :
        return self.dataid( _select, _id)
    def referenceids( self, _select=None) :
        return [ self.referenceid( _select, n_id) for n_id in self.references]

    def datalabel( self, _select, _fmt='%s') :
        if _select is None or _select == () :
            return ''
        return  _fmt % ( ','.join( [ '%s=%s' % ( self._groups[k][0], str( c)) for k, c in enumerate( _select)]))
    def labelat( self, _i, _default=None) :
        if -1 < _i and _i < len( self._labels) :
            return self._labels[_i]
        return _default

    def label( self, _name) :
        try :
            i = self.names.index( _name)
            return  self.labelat( i)
        except ValueError :
            return None

    def __iter__( self) :
        groupcols = [ group[1] for group in self._groups]
        for select in itertools.product( *groupcols) :
            yield select

    def _makeid( self, _id, _ns=None) :
        if _ns is None :
            _ns = self._ns
        if _id is None :
            return '.%s' % ( self._id)
        return '%s.%s' % ( _ns, _id)

    def dependencies( self, _name) :
        return self._exprs.dependencies( _name)
    def expression( self, _name) :
        return self._exprs.expression( _name)

    def add_datasource( self, _name, _datasource) :
        datasource = self._datasources.get( _name)
        if datasource is not None and datasource.name != _datasource.name :
            kklog_warn( 'overwriting datasource (%s) for "%s" in graph "%s"' \
                % ( datasource.name, _name, self.graphid))
        self._datasources[_name] = _datasource
    def get_datasource( self, _name, _warn=True) :
        if self._datasources.get( _name) is None :
            if _warn :
                kklog_warn( 'no datasource for "%s"' % ( _name))
            return None
        return self._datasources[_name]

    @property
    def graphid( self) :
        return self._id
    @property
    def name( self) :
        return self._exprs.name
    @property
    def names( self) :
        return self._exprs.names
    @property
    def NAMES( self) :
        return [ name for name in self._exprs.names if name != self.graphresult]
    @property
    def terminals( self) :
        return self._exprs.terminals
    @property
    def references( self) :
        return [ name for name in self.names if name not in self.terminals+[self.graphresult]]
    @property
    def graphresult( self) :
        return '%s%s%s%s' % ( NSSEP, self.graphid, NSSEP, GRAPHRESULTINTL)
    def is_graphresult( self, _name) :
        return _name == self.graphresult

    @property
    def is_hidden( self) :
        return self.get_property( 'hidden', False)
    @property
    def is_phantom( self) :
        return self.get_property( 'phantom', False)

    def set_domain( self, _domain) :
        self._domain = _domain
    @property
    def domain( self) :
        return self._domain
    @property
    def domainkind( self) :
        return self._domain.kind

    @property
    def zorder( self) :
        return self.get_property( 'index', 0)

    def add_properties( self, _properties) :
        self._properties.update( _properties)
    @property
    def properties( self) :
        return self._properties
    def get_property( self, _property, _default=None) :
        return self._properties.get( _property, _default)

    @property
    def kind( self) :
        return self.get_property( 'kind')
    def get_kindproperty( self, _kindproperty, _default=None) :
        kindproperty = self.get_property( '%sproperties' % ( self.kind))
        if kindproperty :
            return  kindproperty.get( _kindproperty, _default)
        return  _default

    def __str__( self) :
        return 'id=%s; name=%s; label=%s; source=%s; properties=%s' \
            % ( self._id, self.names, self._labels, self._datasources, self.properties)

class kkplot_plot( object) :
    def __init__( self, _id, _title=None, _pos=(0,0), _span=(1,1)) :
        self._id = _id
        self._title = _title
        self._pos = _pos
        self._span = _span

        self._domain = None

        self._properties = dict()

        self._graphs = dict()

    def append_graph( self, _id, _graph) :
        ##kklog_debug( 'adding graph \'%s\'' % ( _id))
        if _id in self._graphs :
            kklog_warn( 'graph \'%s\' already exists, overwriting' % ( _id)) 
        _graph._plot = self
        self._graphs[_id] = _graph
    def get_graph( self, _graphid) :
        return self._graphs.get( _graphid)

    @property
    def id( self) :
        return  self._id
    @property
    def title( self) :
        return  self._title
    @property
    def position_x( self) :
        return  int( self._pos[1])
    @property
    def position_y( self) :
        return  int( self._pos[0])
    @property
    def span_x( self) :
        return  int( self._span[1])
    @property
    def span_y( self) :
        return  int( self._span[0])

    def set_domain( self, _domain) :
        self._domain = _domain
    @property
    def domain( self) :
        return self._domain

    def __iter__( self) :
        for graph in self._graphs.values() :
            yield graph


    def add_properties( self, _properties) :
        self._properties.update( _properties)
    @property
    def properties( self) :
        return self._properties
    def get_property( self, _property, _default=None) :
        return self._properties.get( _property, _default)
    @property
    def get_kindproperties( self) :
        return self.get_property( '%sproperties' % ( self.get_property( 'kind', '*')))
    def get_kindproperty( self, _kindproperty, _default=None) :
        kindproperty = self.get_kindproperties
        if kindproperty :
            return  kindproperty.get( _kindproperty, _default)
        return  _default


    def __str__( self) :
        return 'id=%s; title=%s; pos=%s; domain=%s; graphs=%s' \
            % ( self._id, self._title, self._pos, self.domain, \
            ','.join( [ str(self._graphs[graph]) for graph in self._graphs])) 

class kkplot_graphdependencies( object) :
    def __init__( self, _dependency_graph) :

        refonly_dependency_graph = dict()
        for entity in _dependency_graph :
            refonly_dependency_graph[entity] = list()
            for dep in _dependency_graph[entity] :
                if isreference( dep) :
                    refonly_dependency_graph[entity].append( dep)

        self._dependency_graph = \
            self._topological_sort( refonly_dependency_graph)
        if self._dependency_graph is None :
            raise RuntimeError( 'unresolved dependencies')

    def  _topological_sort( self, _dependency_graph) :
        rc_toposort = "OK"
        dependency_graph = dict()
        rank = 0
        while _dependency_graph :
            dependency_graph[rank] = list()
            for entity in _dependency_graph :
                if len( _dependency_graph[entity]) == 0 :
                    dependency_graph[rank].append( entity)

            for entity in dependency_graph[rank] :
                del _dependency_graph[entity]

            ## if no 'source' exists, and pool is not empty
            if _dependency_graph and ( len( dependency_graph[rank]) == 0) :
                kklog_error( 'dependency-graph: %s' % ( _dependency_graph))
                rc_toposort = "cycle"
                break

            for entity in dependency_graph[rank] :
                for other_entity in _dependency_graph :
                    if entity in _dependency_graph[other_entity] :
                        _dependency_graph[other_entity].remove( entity)

            rank += 1

        if rc_toposort == "OK" :
            #kklog_debug( 'entity-schedule=%s' % ( dependency_graph))
            return dependency_graph
        return  None

    def __iter__( self) :
        for rank in self._dependency_graph :
            for entity in self._dependency_graph[rank] :
                yield entity

    def __len__( self) :
        return sum( [ len( self._dependency_graph[rank]) for rank in self._dependency_graph])

class kkplot_figure( object) :
    def __init__( self, _title=None, _extent=(0,1), _size=None, _outputfile=None, _outputfileformat=None, _components=False) :
        self._title = _title
        self._extent = _extent
        self._size = _size
        self._outputfile = _outputfile if _outputfile else 'kkplot.png'
        self._outputfile = self._outputfile.replace( '\\', '/').strip()
        if _outputfileformat is None :
            of_suffix = self._outputfile.split( '.')
            self._outputfileformat = 'png' if len( of_suffix) < 2 else of_suffix[-1]
        else :
            self._outputfileformat = _outputfileformat
        self._components = _components

        self._plots = dict()
        self._properties = dict()

        self.domain_time = None
        self.domain_space = None
        self.datasource = kkplot_datasource( ':none:')

    ## return set or preferred domain
    @property
    def domain( self) :
        if type( self.domain_time) is kkplot_domains.kkplot_domain_none :
            return self.domain_space
        return self.domain_time

    def append_plot( self, _id, _plot) :
        kklog_debug( 'adding plot \'%s\' with title "%s" at %s, %s' % ( _id, _plot.title, _plot.position_x, _plot.position_y))
        if _id in self._plots :
            kklog_warn( 'plot \'%s\' already exists, overwriting' % ( _id))
        self._plots[_id] = _plot

    def prepare( self) :
        # TODO resolve regular expressions
        #self._resolve_regular_expressions()

        toposorted_entities = self._determine_entity_read_order()
        toposorted_graphs = self._determine_graph_order( toposorted_entities)
        return ( toposorted_entities, toposorted_graphs)

## sk:todo    def _resolve_regular_expressions( self) :
## sk:todo        for plot in self :
## sk:todo            for graph in plot :
## sk:todo                if graph.name is None :
## sk:todo                    continue
## sk:todo                for v in graph.names :
## sk:todo                    kklog_debug( '%s {%s}' % ( v, graph.dependencies( v)))
## sk:todo        sys.exit(1)

    ## sort according to dependencies
    def _determine_entity_read_order( self) :
        entity_graph = dict()
        for plot in self :
            for graph in plot :
                if graph.name is None :
                    continue
                for dataselect in graph :
                    for v in graph.names :
                        entity_graph[v] = graph.dependencies( v)
        return  kkplot_graphdependencies( entity_graph)

    ## sort according to dependencies
    def _determine_graph_order( self, _entities) :
        allgraphs = dict()
        for k, entity in enumerate( _entities) :
            graph = self.get_graph( entity)
            allgraphs[graph.graphid] = ( k, graph)
        sortedgraphs = [ None] * len( _entities)
        for k, graph in allgraphs.values() :
            sortedgraphs[k] = graph
        sortedgraphs = [ graph for graph in sortedgraphs if graph is not None ]
        return  sortedgraphs

    @property
    def title( self) :
        return self._title

    @property
    def extent( self) :
        return self._extent
    @property
    def rows( self) :
        return self._extent[0]
    @property
    def columns( self) :
        return self._extent[1]

    @property
    def size( self) :
        return self._size
    @property
    def height( self) :
        return self._size[0]
    @property
    def width( self) :
        return self._size[1]

    @property
    def outputfile( self) :
        return self._outputfile
    def set_outputfile( self, _outputfile) :
        self._outputfile = _outputfile
    @property
    def outputfileformat( self) :
        return self._outputfileformat
    def set_outputfileformat( self, _outputfileformat) :
        self._outputfileformat = _outputfileformat

    @property
    def components( self) :
        return self._components

    def __iter__( self) :
        for plot in self._plots.values() :
            yield  plot


    def add_properties( self, _properties) :
        self._properties.update( _properties)
    @property
    def properties( self) :
        return self._properties
    def get_property( self, _property, _default=None) :
        return self._properties.get( _property, _default)


    def __str__( self) :
        return 'title=%s; extent=%s; size=%s; output=%s; plots=%s' \
            % ( self._title, self._extent, self._size, self._outputfile, \
                ','.join( [ str( self._plots[plot]) for plot in self._plots]))

    def get_graph( self, _graphpath) :
        graphpath = _graphpath.strip( NSSEP).split( NSSEP)
        if graphpath[0].startswith( DSSEP) :
            graphpath.pop( 0)
        if len( graphpath) < 2 :
            kklog_fatal( 'graph path invalid  [path=%s]' % ( '/'+'/'.join( graphpath)))
        plot = self._plots[graphpath[0]]
        if plot :
            return plot.get_graph( graphpath[1])
        return None

    ## exposed constants
    @property
    def groupbytag( self) :
        return GROUPBYTAG
    @property
    def namespaceseparator( self) :
        return NSSEP
    @property
    def datasourceseparator( self) :
        return DSSEP

    def add_defines( self, _defines) :
        kkplot_defines.add_constants( _defines)

