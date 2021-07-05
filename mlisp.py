"""
A simple one-file LISP interpreter ready for embedding
in a Python program to provide an internal command language.
"""

import sys
import re
import functools
import traceback

class LispError(Exception):
    def __init__(self, msg):
        super(LispError, self).__init__('LISP ERROR: {}'.format(msg))

class LispWrongArgNoError(LispError):
    pass

class LispWrongArgTypeError(LispError):
    pass

class LispReadError(LispError):
    pass

class LispParseError(LispError):
    pass

class LispQuit(Exception):
    pass

def canonical(s):
    return s.lower()


class Environment:
    def __init__(self, bindings=[], previous=None):
        self._previous = previous
        self._bindings = {}
        for(name, value) in bindings:
            self.add(name, value)

    def add(self, symbol, value):
        """
        Add a binding to the current environment
        Replaces old binding if one exists
        """
        symbol = canonical(symbol)
        self._bindings[symbol] = value

    def update(self, symbol, value):
        """
        Update an existing binding
        Look back into higher environments to see
        if it is there
        If not, add it to current environment
        """
        symbol = canonical(symbol)
        if symbol in self._bindings:
            self._bindings[symbol] = value
            return True
        updated = self._previous and self._previous.update(symbol, value)
        if not updated:
            # if the binding doesn't exist, add it locally
            self.add(symbol, value)
        
    def lookup(self, symbol):
        """
        Look for a binding up the environment chain.
        """
        symbol = canonical(symbol)
        if symbol in self._bindings:
            return self._bindings[symbol]
        if self._previous:
            return self._previous.lookup(symbol)
        raise LispError('Cannot find binding for `{}`'.format(symbol))

    def bindings(self):
        return list(self._bindings.items())

    def previous(self):
        return self._previous


class Value:

    def to_list(self, error=True):
        """
        Transforms a LISP list of values into a Python list of values.
        If error is True, raise an exception if not a list, otherwise,
        return None
        """
        if error:
            raise LispError('Not a list: {}'.format(self))
        else:
            return None

    @staticmethod
    def from_tree(struct):
        """
        Transforms a Python tree  of values into a LISP list of values
        """
        if type(struct) == type([]):
            result = VEmpty()
            for r in reversed(struct):
                result = VCons(Value.from_tree(r), result)
            return result
        else:
            return struct

    def _str_cdr(self):
        raise LispError('Cannot use value as list terminator: {}'.format(self))

    def display(self):
        return str(self)

    def pp(self, prefix=0, suffix='', skip_prefix=False):
        if skip_prefix:
            return str(self) + suffix
        else:
            return(' ' * prefix) + str(self) + suffix

    def kind(self):
        return None

    def is_number(self):
        return self.kind() == 'number'

    def is_boolean(self):
        return self.kind() == 'boolean'

    def is_string(self):
        return self.kind() == 'string'

    def is_symbol(self):
        return self.kind() == 'symbol'

    def is_nil(self):
        return self.kind() == 'nil'

    def is_empty(self):
        return self.kind() == 'empty-list'
    
    def is_cons(self):
        return self.kind() == 'cons-list'

    def is_function(self):
        return self.kind() in('primitive', 'function')

    def is_atom(self):
        # only really makes sense for things that are readable
        return self.kind() in ['number', 'symbol', 'string', 'boolean']

    def is_list(self):
        return self.kind() in ['empty-list', 'cons-list']
    
    def is_true(self):
        return True

    def is_equal(self, v):
        # by default, do is_eq
        return self.is_eq(v)

    def is_eq(self, v):
        # "pointer" equality
        ##self.kind() == v.kind() and self.value() == v.value()
        return id(self) == id(v)

    def apply(self, args):
        raise LispError('Cannot apply value {}'.format(self))

    
class VBoolean(Value):
    def __init__(self, b):
        self._value = b

    def __repr__(self):
        return 'VBoolean({})'.format(self._value)

    def __str__(self):
        return '#true' if self._value else '#false'

    def kind(self):
        return 'boolean'

    def value(self):
        return self._value

    def is_true(self):
        return self._value
        
    def is_eq(self, v):
        return v.is_boolean() and self.value() == v.value()

    
class VString(Value):
    def __init__(self, s):
        self._value = s

    def __repr__(self):
        return 'VString({})'.format(self._value)

    def __str__(self):
        return '"{}"'.format(self._value)

    def kind(self):
        return 'string'

    def display(self):
        return self._value.replace('\\"', '"').replace('\\t', '\t').replace('\\n', '\n').replace('\\\\','\\')

    def value(self):
        return self._value
        
    def is_true(self):
        return not(not self._value)
        
    def is_equal(self, v):
        return v.is_string() and self.value() == v.value()
    
    
class VNumber(Value):
    def __init__(self, v):
        self._value = v

    def __repr__(self):
        return 'VNumber({})'.format(self._value)

    def __str__(self):
        return str(self._value)

    def kind(self):
        return 'number'

    def value(self):
        return self._value

    def is_true(self):
        return not(not self._value)
        
    def is_eq(self, v):
        return v.is_number() and self.value() == v.value()


class VNil(Value):
    def __repr__(self):
        return 'VNil()'

    def __str__(self):
        return '#nil'

    def kind(self):
        return 'nil'

    def is_true(self):
        return False

    def value(self):
        return None

    def is_eq(self, v):
        return v.is_nil()


class VEmpty(Value):
    def __repr__(self):
        return 'VEmpty()'

    def to_list(self, error=True):
        return []
    
    def __str__(self):
        return '()'

    def _str_cdr(self):
        return ')'

    def kind(self):
        return 'empty-list'

    def is_true(self):
        return False

    def value(self):
        return None

    def is_eq(self, v):
        return v.is_empty()

    
class VCons(Value):
    def __init__(self, car, cdr):
        if not cdr.is_list():
            raise LispError('List required as second cons argument')
        self._car = car
        self._cdr = cdr

    def to_list(self, error=True):
        curr = self
        result = []
        while curr.kind() == 'cons-list':
            result.append(curr.car())
            curr = curr.cdr()
        return result
    
    def __repr__(self):
        return 'VCons({},{})'.format(repr(self._car), repr(self._cdr))

    def __str__(self):
        return '({}{}'.format(self._car, self._cdr._str_cdr())

    def _str_cdr(self):
        return ' {}{}'.format(self._car, self._cdr._str_cdr())

    def pp(self, prefix=0, suffix='', skip_prefix=False):
        result = ''
        if not skip_prefix:
            result += ' ' * prefix
        result += '('
        lst = self.to_list()
        for i, v in enumerate(lst):
            skip =(i == 0)
            last =(i == len(lst) - 1)
            sub_suffix = ')' + suffix if last else '\n'
            result += v.pp(prefix=prefix + 1, skip_prefix=skip, suffix=sub_suffix)
        return result
    
    def kind(self):
        return 'cons-list'

    def value(self):
        return(self._car, self._cdr)

    def car(self):
        return self._car

    def cdr(self):
        return self._cdr

    def is_equal(self, v):
        return v.is_cons() and self.car().is_equal(v.car()) and self.cdr().is_equal(v.cdr())
    

class VPrimitive(Value):
    def __init__(self, name, primitive, min, max=None):
        self._name = name
        self._primitive = primitive
        self._min = min
        self._max = max
        
    def __repr__(self):
        return 'VPrimitive({})'.format(self._primitive.__name__)

    def __str__(self):
        h = id(self)
        return '#[prim {}]'.format(hex(h))

    def kind(self):
        return 'primitive'

    def value(self):
        return self._primitive

    def apply(self, values):
        if len(values) < self._min:
            raise LispWrongArgNoError('Too few arguments {} to primitive {}'.format(len(values), self._name))
        if self._max and len(values) > self._max:
            raise LispWrongArgNoError('Too many arguments {} to primitive {}'.format(len(values), self._name))
        result = self._primitive(self._name, values)
        return(result or VNil())
    
    
class VSymbol(Value):
    def __init__(self, sym):
        self._symbol = canonical(sym)

    def __repr__(self):
        return 'VSymbol({})'.format(self._symbol)

    def __str__(self):
        return self._symbol

    def kind(self):
        return 'symbol'

    def value(self):
        return self._symbol

    def is_eq(self, v):
        return v.is_symbol() and self.value() == v.value()
    
    
class VFunction(Value):
    def __init__(self, params, body, env):
        self._params = params
        self._body = body
        self._env = env

    def __repr__(self):
        return 'VFunction({}, {})'.format(self._params, repr(self._body))

    def __str__(self):
        h = id(self)
        return '#[func {}]'.format(hex(h))

    def binding_env(self, values):
        if len(self._params) != len(values):
            raise LispWrongArgNoError('Wrong number of arguments to {}'.format(self))
        params_bindings = list(zip(self._params, values))
        new_env = Environment(previous=self._env)
        for(x, y) in params_bindings:
            new_env.add(x, y)
        return new_env

    def apply(self, values):
        new_env = self.binding_env(values)
        return self._body.eval(new_env)

    def kind(self):
        return 'function'

    def value(self):
        return(self._params, self._body, self._env)



class Expression:

    def eval_partial(self, env):
        """ 
        Partial evaluation.
        Sometimes return an expression to evaluate next along 
        with an environment for evaluation.
        Environment is None when the result is in fact a value.
        """
        return(self.eval(env), None)

    def eval(self, env):
        """
        Evaluation with tail-call optimization.
        """
        curr_exp = self
        curr_env = env

        while(True):
            (new_exp, new_env) = curr_exp.eval_partial(curr_env)
            if new_env is None:
                # actually a value!
                return new_exp
            curr_exp = new_exp
            curr_env = new_env
    
    
class Symbol(Expression):
    def __init__(self, sym):
        self._symbol = canonical(sym)

    def __repr__(self):
        return 'Symbol({})'.format(self._symbol)

    def eval(self, env):
        v = env.lookup(self._symbol)
        if v is None:
            raise LispError('Trying to access a non-initialized binding {} in a LETREC'.format(self._symbol))
        return env.lookup(self._symbol)


class String(Expression):
    def __init__(self, s):
        self._string = s

    def __repr__(self):
        return 'String({})'.format(self._string)
                           
    def eval(self, env):
        return VString(self._string)
                            
    
class Integer(Expression):
    def __init__(self, s):
        self._value = int(s)

    def __repr__(self):
        return 'Integer({})'.format(self._value)
                            
    def eval(self, env):
        return VNumber(self._value)

    
class Boolean(Expression):
    def __init__(self, b):
        self._value = b

    def __repr__(self):
        return 'Boolean({})'.format(self._value)
                            
    def eval(self, env):
        return VBoolean(self._value)

    
class Apply(Expression):
    def __init__(self, fun, args):
        self._fun = fun
        self._args = args
        
    def __repr__(self):
        return 'Apply({}, [{}])'.format(repr(self._fun),
                                        ', '.join([ repr(arg) for arg in self._args ]))

    def eval_partial(self, env):
        f = self._fun.eval(env)
        values = [ arg.eval(env) for arg in self._args ]
        if isinstance(f, VPrimitive):
            return(f.apply(values), None)
        elif isinstance(f, VFunction):
            (_, body, _) = f.value()
            new_env = f.binding_env(values)
            return(body, new_env)
        else:
            raise LispError('Cannot apply value {}'.format(f))
    
    
class If(Expression):
    def __init__(self, cnd, thn, els):
        self._cond = cnd
        self._then = thn
        self._else = els

    def __repr__(self):
        return 'If({}, {}, {})'.format(repr(self._cond),
                                       repr(self._then),
                                       repr(self._else))
        
    def eval_partial(self, env):
        c = self._cond.eval(env)
        if c.is_true():
            return(self._then, env)
        else:
            return(self._else, env)

        
class Quote(Expression):
    def __init__(self, sexpr):
        self._sexpr = sexpr

    def __repr__(self):
        return 'Quote({})'.format(repr(self._sexpr))

    def eval(self, env):
        return self._sexpr


class Lambda(Expression):
    def __init__(self, params, expr):
        self._params = [ canonical(p) for p in params ]
        self._expr = expr

    def __repr__(self):
        return 'Lambda({}, {})'.format(self._params, repr(self._expr))
        
    def eval(self, env):
        return VFunction(self._params, self._expr, env)

    
class LetRec(Expression):
    def __init__(self, bindings, expr):
        self._bindings = bindings
        self._expr = expr

    def __repr__(self):
        return 'LetRec({}, {})'.format([(x, repr(z)) for(x, z) in self._bindings ], repr(self._expr))

    def eval_partial(self, env):
        new_env = Environment(previous=env)
        for(n, e) in self._bindings:
            new_env.add(n, None)
        vs = [ e.eval(new_env) for(_, e) in self._bindings ]
        for((n, _), v) in zip(self._bindings, vs):
            new_env.add(n, v)
        return(self._expr, new_env)
            

class Do(Expression):
    def __init__(self, exprs):
        self._exprs = exprs
        
    def __repr__(self):
        return 'Do([{}])'.format(', '.join([ repr(arg) for arg in self._exprs ]))
        
    def eval_partial(self, env):
        if not self._exprs:
            return(VNil(), None)
        for expr in self._exprs[:-1]:
            expr.eval(env)
        return(self._exprs[-1], env)




# PARSER COMBINATORS

# a parser is a function String -> Option('a, String)

# perhaps create a ParserComponent class acting as a decorator
# to have + and | and > as possible combinators?
# cf: http://tomerfiliba.com/blog/Infix-Operators/

def parse_wrap(p, f):

    def parser(s):
        result = p(s)
        if result is None:
            return None
        return f(result)

    return parser


def parse_seq(ps):

    def parser(s):
        acc_result = []
        current = s
        for p in ps:
            result = p(current)
            if result is None:
                return None
            acc_result.append(result[0])
            current = result[1]
        return(acc_result, current)

    return parser


def parse_first(ps):

    def parser(s):
        for p in ps:
            result = p(s)
            if result is not None:
                return result
        return None

    return parser


def parse_sexp_wrap(p, f):
    def parser(s):
        result = p(s)
        if not result:
            return None
        return (f(result[0]), result[1])
    return parser



class Reader:

    def __init__(self):
        self._macros = {}

    def register_macro(self, name, transform):
        name = name.lower()
        if name in self._macros:
            raise LispError('Macro {} already exists'.format(name))
        self._macros[name] = transform

        
    # SEXPRESSIONS parser

    def parse_token(self, token):
        def parser(s):
            ss = s.strip()
            m = re.match(token, ss)
            if m:
                return(m.group(), ss[m.end():])
            return None
        return parser

    def parse_success(self, v):
        def parser(s):
            return(v, s)
        return parser

    def parse_lparen(self, s):
        return self.parse_token(r'\(')(s)

    def parse_rparen(self, s):
        return self.parse_token(r'\)')(s)

    def parse_dot(self, s):
        return self.parse_token(r'\.')(s)

    def parse_number(self, s):
        p = self.parse_token(r'-?[0-9]+')
        return parse_sexp_wrap(p, lambda x: VNumber(int(x)))(s)
    
    def parse_symbol(self, s):
        identifier = r'[^"\s#()]+'   # [A-Za-z0-9-+/*_:.?!@$]*[A-Za-z-+/*_:.?!@$#][A-Za-z0-9-+/*_:.?!@$]*'
        p = self.parse_token(identifier)
        return parse_sexp_wrap(p, lambda x: VSymbol(x))(s)

    def parse_string(self, s):
        def clean(s):
            return s.replace('\\"', '"').replace('\\\\', '\\')
        # p = parse_token(r'"[^"]*"')
        p = self.parse_token(r'"(?:[^"\\]|\\.)*"')
        return parse_sexp_wrap(p, lambda x: VString(x[1:-1]))(s)

    def parse_boolean(self, s):
        p = self.parse_token(r'#([tT][rR][uU][eE])|#([fF][aA][lL][sS][eE])')
        return parse_sexp_wrap(p, lambda x: VBoolean(x.lower() == '#true'))(s)

    def parse_sexp(self, s):
        p = parse_first([self.parse_number,
                         self.parse_string,
                         self.parse_boolean,
                         self.parse_symbol,
                         self.parse_macros,
                         parse_sexp_wrap(parse_seq([self.parse_token(r"'"),
                                                    self.parse_sexp]),
                                         lambda x: VCons(VSymbol('quote'), VCons(x[1], VEmpty()))),
                         parse_sexp_wrap(parse_seq([self.parse_lparen,
                                                    self.parse_sexps,
                                                    self.parse_rparen]),
                                         lambda x: x[1])])
        return p(s)

    def parse_sexps(self, s):
        p = parse_first([parse_sexp_wrap(parse_seq([self.parse_sexp,
                                                    self.parse_sexps]),
                                         lambda x: VCons(x[0], x[1])),
                         self.parse_success(VEmpty())])
        return p(s)

    
    def parse_hash_lparen(self, s):
        return self.parse_token(r'#\(')(s)

    
    def parse_macro_name(self, name):
        cname = canonical(name)
        def parser(s):
            ss = s.strip()
            if canonical(ss).startswith(cname):
                return(cname, ss[len(cname):])
            return None
        return parser

    
    def parse_macros(self, s):
        parsers = [parse_sexp_wrap(parse_seq([self.parse_hash_lparen,
                                              self.parse_macro_name(m),
                                              self.parse_sexps,
                                              self.parse_rparen]),
                                   lambda x:(x[1], x[2])) for m in self._macros]
        p = parse_first(parsers)
        result = p(s)
        if result:
            # we got a match, so one of the macros must have matched
            # this commits us
            ((name, exps), rest) = result
            return (self._macros[name](self, name, exps), rest)
        return None
    

class Parser:
    def __init__(self):
        self._macros = {}
        self._gensym_count = 0

    def register_macro(self, name, transform):
        name = name.lower()
        if name in self._macros:
            raise LispError('Macro {} already exists'.format(name))
        self._macros[name] = transform

    def gensym(self, prefix='gsym'):
        c = self._gensym_count
        self._gensym_count += 1
        return ' __{}_{}'.format(prefix, c)

    def parse(self, sexp):
        result = self.parse_define(sexp)
        if result:
            return('define', result)
        result = self.parse_defun(sexp)
        if result:
            return('defun', result)
        result = self.parse_exp(sexp)
        if result:
            return('exp', result)
        raise LispParseError('Cannot parse {}'.format(sexp))
        
    def parse_atom(self, s):
        if not s:
            return None
        if s.is_atom():
            if s.is_number():
                return Integer(s.value())
            if s.is_symbol():
                return Symbol(s.value())
            if s.is_string():
                return String(s.value())
            if s.is_boolean():
                return Boolean(s.value())
            raise LispParseError('Cannot parse atom {}'.format(s))
        return None


    def parse_empty(self, s):
        return [] if s.is_empty() else None


    def parse_list(self, ps, tail=None):

        ptail = tail if tail else self.parse_empty

        def parser(s):
            current = s
            acc = []
            for p in ps:
                if current.is_cons():
                    (car, cdr) = current.value()
                    e = p(car)
                    if e is None:
                        return None
                    acc.append(e)
                    current = cdr
                else:
                    return None
            last = ptail(current)
            if last is None:
                return None
            if tail:
                return(acc, last)
            else:
                return acc

        return parser


    def parse_rep(self, p, tail=None):

        ptail = tail if tail else self.parse_empty

        def parser(s):
            current = s
            acc = []
            while current.is_cons():
                (car, cdr) = current.value()
                e = p(car)
                if e is None:
                    return None
                acc.append(e)
                current = cdr
            last = ptail(current)
            if last is None:
                return None
            if tail:
                return(acc, last)
            else:
                return acc

        return parser


    def parse_rep1(self, p, tail=None):

        ptail = tail if tail else self.parse_empty

        def parser(s):
            # at least 1
            if not s.is_cons():
                return None
            (car, cdr) = s.value()
            e = p(car)
            if e is None:
                return None
            acc = [e]
            current = cdr
            while current.is_cons():
                (car, cdr) = current.value()
                e = p(car)
                if e is None:
                    return None
                acc.append(e)
                current = cdr
            last = ptail(current)
            if last is None:
                return None
            if tail:
                return(acc, last)
            else:
                return acc

        return parser
    
    
    def parse_keyword(self, kw):

        def parser(s):
            if not s:
                return None
            if s.is_symbol() and canonical(s.value()) == canonical(kw):
                return canonical(kw)
            return None

        return parser


    def parse_identifier(self, s):

        if not s:
            return None
        if s.is_symbol():
            # should check it is not a keyword?
            return s.value()
        return None


    def parse_exp(self, s):

        p = parse_first([self.parse_atom,
                         self.parse_quote,
                         self.parse_if,
                         self.parse_lambda,
                         self.parse_do,
                         self.parse_letrec,
                         self.parse_macros,
                         self.parse_apply])
        return p(s)


    def parse_if(self, s):

        p = self.parse_list([self.parse_keyword('if'),
                             self.parse_exp,
                             self.parse_exp,
                             self.parse_exp])
        p = parse_wrap(p, lambda x: If(x[1], x[2], x[3]))
        return p(s)


    def parse_lambda(self, s):

        p = self.parse_list([self.parse_keyword('fn'),
                             self.parse_rep(self.parse_identifier)],
                            tail=self.parse_exps)
        p = parse_wrap(p, lambda x:Lambda(x[0][1], Do(x[1])))
        return p(s)

    
    def parse_do(self, s):

        p = self.parse_list([self.parse_keyword('do')],
                            tail=self.parse_exps)
        p = parse_wrap(p, lambda x: Do(x[1]))
        return p(s)


    def parse_quote(self, s):

        p = self.parse_list([self.parse_keyword('quote'),
                             lambda s: s])
        p = parse_wrap(p, lambda x: Quote(x[1]))
        return p(s)


    def parse_letrec(self, s):
        p = self.parse_list([self.parse_keyword('letrec'),
                             self.parse_rep(self.parse_binding)],
                            tail=self.parse_exps)
        p = parse_wrap(p, lambda x: LetRec(x[0][1], Do(x[1])))
        return p(s)

    
    def parse_apply(self, s):

        p = self.parse_rep1(self.parse_exp)
        p = parse_wrap(p, lambda x: Apply(x[0], x[1:]))
        return p(s)


    def parse_exps(self, s):

        p = self.parse_rep(self.parse_exp)
        return p(s)

    
    def parse_binding(self, s):
        p = self.parse_list([self.parse_identifier,
                        self.parse_exp])
        p = parse_wrap(p, lambda x:(x[0], x[1]))
        return p(s)

    
    def parse_macros(self, s):
        parsers = [parse_wrap(self.parse_list([self.parse_keyword(m)],
                                              tail=lambda ss:ss),
                              lambda x:(x[0][0], x[1])) for m in self._macros]
        p = parse_first(parsers)
        result = p(s)
        if result:
            # we got a match, so one of the macros must have matched
            # this commits us
            (name, exps) = result
            new_exp = self._macros[name](self, name, exps)
            return self.parse_exp(new_exp)
        return None

    
    ############################################################
    #
    # Top level commands
    #

    def parse_define(self, s):
        p = self.parse_list([self.parse_keyword('def'),
                             self.parse_identifier,
                             self.parse_exp])
        p = parse_wrap(p, lambda x:(x[1], x[2]))
        return p(s)


    def parse_defun(self, s):
        p = self.parse_list([self.parse_keyword('def'),
                              self.parse_list([self.parse_identifier],
                                              tail=self.parse_rep(self.parse_identifier))],
                             tail=self.parse_exps)
        p = parse_wrap(p, lambda x:(x[0][1][0][0], x[0][1][1], Do(x[1])))
        return p(s)


_PRIMITIVES = []

def check_arg_type(name, v, pred):
    if not pred(v):
        raise LispWrongArgTypeError('Wrong argument type {} to primitive {}'.format(v, name))

def primitive(name, min, max=None):
    name = canonical(name)
    def decorator(func):
        _PRIMITIVES.append((name, VPrimitive(name, func, min, max)))
        return func
    return decorator


@primitive('type', 1, 1)
def prim_type(name, args):
    return VSymbol(args[0].kind())


@primitive('+', 0)
def prim_plus(name, args):
    v = 0
    for arg in args:
        check_arg_type(name, arg, lambda v:v.is_number())
        v += arg.value()
    return VNumber(v)

@primitive('*', 0)
def prim_times(name, args):
    v = 1
    for arg in args:
        check_arg_type(name, arg, lambda v:v.is_number())
        v *= arg.value()
    return VNumber(v)

@primitive('-', 1)
def prim_minus(name, args):
    check_arg_type(name, args[0], lambda v:v.is_number())
    v = args[0].value()
    if args[1:]:
        for arg in args[1:]:
            check_arg_type(name, arg, lambda v:v.is_number())
            v -= arg.value()
        return VNumber(v)
    else:
        return VNumber(-v)

def _num_predicate(arg1, arg2, sym, pred):
    check_arg_type(sym, arg1, lambda v:v.is_number())
    check_arg_type(sym, arg2, lambda v:v.is_number())
    return VBoolean(pred(arg1.value(), arg2.value()))
    
@primitive('=', 2, 2)
def prim_numequal(name, args):
    return _num_predicate(args[0], args[1], name, lambda v1, v2: v1 == v2)

@primitive('<', 2, 2)
def prim_numless(name, args):
    return _num_predicate(args[0], args[1], name, lambda v1, v2: v1 < v2)

@primitive('<=', 2, 2)
def prim_numlesseq(name, args):
    return _num_predicate(args[0], args[1], name, lambda v1, v2: v1 <= v2)

@primitive('>', 2, 2)
def prim_numgreater(name, args):
    return _num_predicate(args[0], args[1], name, lambda v1, v2: v1 > v2)

@primitive('>=', 2, 2)
def prim_numgreatereq(name, args):
    return _num_predicate(args[0], args[1], name, lambda v1, v2: v1 >= v2)

@primitive('not', 1, 1)
def prim_not(name, args):
    return VBoolean(not args[0].is_true())

@primitive('string-append', 0)
def prim_string_append(name, args):
    v = ''
    for arg in args:
        check_arg_type(name, arg, lambda v:v.is_string())
        v += arg.value()
    return VString(v)

@primitive('string-length', 1, 1)
def prim_string_length(name, args):
    check_arg_type(name, args[0], lambda v:v.is_string())
    return VNumber(len(args[0].value()))

@primitive('string-lower', 1, 1)
def prim_string_lower(name, args):
    check_arg_type(name, args[0], lambda v:v.is_string())
    return VString(args[0].value().lower())

@primitive('string-upper', 1, 1)
def prim_string_upper(name, args):
    check_arg_type(name, args[0], lambda v:v.is_string())
    return VString(args[0].value().upper())

@primitive('string-substring', 1, 3)
def prim_string_substring(name, args):
    check_arg_type(name, args[0], lambda v:v.is_string())
    if len(args) > 2:
        check_arg_type(name, args[2], lambda v:v.is_number())
        end = args[2].value()
    else:
        end = len(args[0].value())
    if len(args) > 1:
        check_arg_type(name, args[1], lambda v:v.is_number())
        start = args[1].value()
    else:
        start = 0
    return VString(args[0].value()[start:end])

@primitive('apply', 2, 2)
def prim_apply(name, args):
    check_arg_type(name, args[0], lambda v:v.is_function())
    check_arg_type(name, args[1], lambda v:v.is_list())
    return args[0].apply(args[1].to_list())
    
@primitive('cons', 2, 2)
def prim_cons(name, args):
    check_arg_type(name, args[1], lambda v:v.is_list())
    return VCons(args[0], args[1])

@primitive('append', 0)
def prim_append(name, args):
    v = VEmpty()
    for arg in reversed(args):
        check_arg_type(name, arg, lambda v:v.is_list())
        curr = arg
        temp = []
        while not curr.is_empty():
            temp.append(curr.car())
            curr = curr.cdr()
        for t in reversed(temp):
            v = VCons(t, v)
    return v

@primitive('reverse', 1, 1)
def prim_reverse(name, args):
    check_arg_type(name, args[0], lambda v:v.is_list())
    v = VEmpty()
    curr = args[0]
    while not curr.is_empty():
        v = VCons(curr.car(), v)
        curr = curr.cdr()
    return v

@primitive('first', 1, 1)
def prim_first(name, args):
    check_arg_type(name, args[0], lambda v:v.is_cons())
    return args[0].car()

@primitive('rest', 1, 1)
def prim_rest(name, args):
    check_arg_type(name, args[0], lambda v:v.is_cons())
    return args[0].cdr()

@primitive('list', 0)
def prim_list(name, args):
    v = VEmpty()
    for arg in reversed(args):
        v = VCons(arg, v)
    return v

@primitive('length', 1, 1)
def prim_length(name, args):
    check_arg_type(name, args[0], lambda v:v.is_list())
    count = 0
    curr = args[0]
    while not curr.is_empty():
        count += 1
        curr = curr.cdr()
    return VNumber(count)

@primitive('nth', 2, 2)
def prim_nth(name, args):
    check_arg_type(name, args[0], lambda v:v.is_list())
    check_arg_type('nth', args[1], lambda v:v.is_number())
    idx = args[1].value()
    curr = args[0]
    while not curr.is_empty():
        if idx:
            idx -= 1
            curr = curr.cdr()
        else:
            return curr.car()
    raise LispError('Index out of range of list')

@primitive('map', 2)
def prim_map(name, args):
    check_arg_type(name, args[0], lambda v:v.is_function())
    for arg in args[1:]:
        check_arg_type(name, arg, lambda v:v.is_list())
    temp = []
    currs = args[1:]
    while all(curr.is_cons() for curr in currs):
        firsts = [ curr.car() for curr in currs ]
        currs = [ curr.cdr() for curr in currs ]
        temp.append(args[0].apply(firsts))
    v = VEmpty()
    for t in reversed(temp):
        v = VCons(t, v)
    return v

@primitive('filter', 2, 2)
def prim_filter(name, args):
    check_arg_type(name, args[0], lambda v:v.is_function())
    check_arg_type(name, args[1], lambda v:v.is_list())
    temp = []
    curr = args[1]
    while not curr.is_empty():
        if args[0].apply([curr.car()]).is_true():
            temp.append(curr.car())
        curr = curr.cdr()
    v = VEmpty()
    for t in reversed(temp):
        v = VCons(t, v)
    return v

@primitive('foldr', 3, 3)
def prim_foldr(name, args):
    check_arg_type(name, args[0], lambda v:v.is_function())
    check_arg_type(name, args[1], lambda v:v.is_list())
    curr = args[1]
    temp = []
    while not curr.is_empty():
        temp.append(curr.car())
        curr = curr.cdr()
    v = args[2]
    for t in reversed(temp):
        v = args[0].apply([t, v])
    return v

@primitive('foldl', 3, 3)
def prim_foldl(name, args):
    check_arg_type(name, args[0], lambda v:v.is_function())
    check_arg_type(name, args[2], lambda v:v.is_list())
    curr = args[2]
    v = args[1]
    while not curr.is_empty():
        v = args[0].apply([v, curr.car()])
        curr = curr.cdr()
    return v

@primitive('eq?', 2, 2)
def prim_eqp(name, args):
    return VBoolean(args[0].is_eq(args[1]))

@primitive('eql?', 2, 2)
def prim_eqlp(name, args):
    return VBoolean(args[0].is_equal(args[1]))

@primitive('empty?', 1, 1)
def prim_emptyp(name, args):
    return VBoolean(args[0].is_empty())
    
@primitive('cons?', 1, 1)
def prim_consp(name, args):
    return VBoolean(args[0].is_cons())

@primitive('list?', 1, 1)
def prim_listp(name, args):
    return VBoolean(args[0].is_list())

@primitive('number?', 1, 1)
def prim_numberp(name, args):
    return VBoolean(args[0].is_number())

@primitive('boolean?', 1, 1)
def prim_booleanp(name, args):
    return VBoolean(args[0].is_boolean())

@primitive('string?', 1, 1)
def prim_stringp(name, args):
    return VBoolean(args[0].is_string())

@primitive('symbol?', 1, 1)
def prim_symbolp(name, args):
    return VBoolean(args[0].is_symbol())

@primitive('function?', 1, 1)
def prim_functionp(name, args):
    return VBoolean(args[0].is_function())

@primitive('nil?', 1, 1)
def prim_nilp(name, args):
    return VBoolean(args[0].is_nil())


def macro_let(parser, name, exps):
    expr = VCons(VSymbol(name), exps)
    exps = exps.to_list()
    if len(exps) != 2:
        raise LispParseError('Cannot parse `{}`: too {} subexpressions in {}'.format(name, 'many' if len(exps) > 2 else 'few', expr))
    body = exps[1]
    bindings = exps[0].to_list(error=False)
    if bindings is None:
        raise LispParseError('Cannot parse `{}`: bindings not a list in {}'.format(name, expr))
    params = []
    args = []
    for bindingV in bindings:
        binding = bindingV.to_list(error=False)
        if binding is None:
            raise LispParseError('Cannot parse `{}`: binding {} not a list'.format(name, bindingV))
        if len(binding) != 2:
            raise LispParseError('Cannot parse `{}`: too {} subexpressions in binding {}'.format(name, 'many' if len(binding) > 2 else 'few', bindingV))
        if not binding[0].is_symbol():
            raise LispParseError('Cannot parse `{}`: binding name not a symbol in {}'.format(name, bindingV))
        params.append(binding[0])
        args.append(binding[1])
    result = Value.from_tree([[VSymbol('fn'), params, body]] + args)
    ##print('Expansion:', str(result))
    return result


def macro_letstar(parser, name, exps):
    expr = VCons(VSymbol(name), exps)
    exps = exps.to_list()
    if len(exps) != 2:
        raise LispParseError('Cannot parse `{}`: too {} subexpressions in {}'.format(name, 'many' if len(exps) > 2 else 'few', expr))
    result = exps[1]
    bindings = exps[0].to_list(error=False)
    if bindings is None:
        raise LispParseError('Cannot parse `{}`: bindings not a list in {}'.format(name, expr))
    for bindingV in reversed(bindings):
        binding = bindingV.to_list(error=False)
        if binding is None:
            raise LispParseError('Cannot parse `{}`: binding {} not a list'.format(name, bindingV))
        if len(binding) != 2:
            raise LispParseError('Cannot parse `{}`: too {} subexpressions in binding {}'.format(name, 'many' if len(binding) > 2 else 'few', bindingV))
        if not binding[0].is_symbol():
            raise LispParseError('Cannot parse `{}`: binding name not a symbol in {}'.format(name, bindingV))
        result = Value.from_tree([VSymbol('let'),
                                  [bindingV],
                                  result])
    ##print('Expansion:', str(result))
    return result


def macro_and(parser, name, exps):
    exps = exps.to_list()
    if exps:
        result = exps[-1]
        for e in reversed(exps[:-1]):
            n = parser.gensym()
            result = Value.from_tree([VSymbol('let'),
                                      [[VSymbol(n), e]],
                                      [VSymbol('if'), VSymbol(n), result, VSymbol(n)]])
    else:
        result = VBoolean(True)
    ##print('Expansion:', str(result))
    return result


def macro_or(parser, name, exps):
    exps = exps.to_list()
    if exps:
        result = exps[-1]
        for e in reversed(exps[:-1]):
            n = parser.gensym()
            result = Value.from_tree([VSymbol('let'),
                                      [[VSymbol(n), e]],
                                      [VSymbol('if'), VSymbol(n), VSymbol(n), result]])
    else:
        result = VBoolean(False)
    ##print('Expansion:', str(result))
    return result


#
# Sample extension: references
#

class VReference(Value):
    def __init__(self, v):
        self._value = v

    def __repr__(self):
        return 'VReference({})'.format(self._value)

    def __str__(self):
        return '#(ref {})'.format(self._value)

    def kind(self):
        return 'reference'

    def value(self):
        return self._value

    def set_value(self, v):
        self._value = v

    def is_equal(self, v):
        # ??
        return v.kind() == 'reference' and self.value().is_equal(v.value())

def prim_refp(name, args):
    return VBoolean(args[0].kind() == 'reference')

def prim_ref(name, args):
    return VReference(args[0])

def prim_ref_get(name, args):
    check_arg_type(name, args[0], lambda v: v.kind() == 'reference')
    return args[0].value()

def prim_ref_set(name, args):
    check_arg_type(name, args[0], lambda v: v.kind() == 'reference')
    args[0].set_value(args[1])
    return VNil()

def reader_ref(reader, name, exps):
    exps = exps.to_list()
    if len(exps) != 1:
        raise LispReadError('Cannot read `{}`: too {} items'.format(name, 'many' if len(exps) > 1 else 'few'))
    return Value.from_tree([VSymbol('ref'), exps[0]])


class Engine:
    def __init__(self):
        # basic environment
        self._env = Environment(bindings=_PRIMITIVES)
        self._parser = Parser()
        self._reader = Reader()
        self._prompt = '>'
        self.def_value('true', VBoolean(True))
        self.def_value('false', VBoolean(False))
        self.def_value('empty', VEmpty())
        self.def_value('nil', VNil())
        self.def_primitive('print', self.prim_print, 0, None)
        # sample macros
        self.register_macro('let', macro_let)
        self.register_macro('let*', macro_letstar)
        self.register_macro('and', macro_and)
        self.register_macro('or', macro_or)
        # references
        self.def_primitive('ref?', prim_refp, 1, 1)
        self.def_primitive('ref', prim_ref, 1, 1)
        self.def_primitive('ref-get', prim_ref_get, 1, 1)
        self.def_primitive('ref-set!', prim_ref_set, 2, 2)
        self.register_reader('ref', reader_ref)

    def prompt(self, prompt):
        self._prompt = prompt
        return self

    def new_env(self, bindings=[]):
        self._env = Environment(bindings=bindings, previous=self._env)
        return self

    def def_value(self, name, value):
        self._env.add(name, value)

    def def_primitive(self, name, prim, min, max):
        self._env.add(name, VPrimitive(name, prim, min, max))

    def register_macro(self, name, macro):
        self._parser.register_macro(name, macro)

    def register_reader(self, name, macro):
        self._reader.register_macro(name, macro)

    def prim_print(self, name, args):
        result = ' '.join([arg.display() for arg in args])
        self.emit(result)

    def read(self, s):
        if not s.strip():
            return None
        result = self._reader.parse_sexp(s)
        if result:
            return result[0]
        raise LispReadError('Cannot read {}'.format(s))
        
    def eval(self, sexp, report=False):
        (kind, result) = self._parser.parse(sexp)
        if kind == 'define':
            (name, expr) = result
            name = canonical(name)
            v = expr.eval(self._env)
            self._env.add(name, v)
            if report:
                self.emit_report(name)
            return VNil()
        if kind == 'defun':
            (name, params, expr) = result
            params = [ canonical(p) for p in params ]
            v = VFunction(params, expr, self._env)
            self._env.add(name, v)
            if report:
                self.emit_report(name)
            return VNil()
        if kind == 'exp':
            return result.eval(self._env)
        raise LispError('Cannot recognize top level kind {}'.format(kind))

    def balance(self, str):
        state = 'normal'
        count = 0
        pos = 0
        while pos < len(str):
            if state == 'normal':
                if str[pos] == '(':
                    pos += 1
                    count += 1
                elif str[pos] == ')':
                    pos += 1
                    count -= 1
                elif str[pos] == '"':
                    pos += 1
                    state = 'string'
                else:
                    pos += 1
            elif state == 'string':
                if str[pos] == '"':
                    pos += 1
                    state = 'normal'
                elif str[pos] == '\\':
                    pos += 1
                    state = 'escape'
                elif str[pos] == '\n':
                    raise LispParseError('Unterminated string')
                else:
                    pos += 1
            elif state == 'escape':
                pos += 1
                state = 'string'
        # this will ignore inputs past the end of the first expression
        return count <= 0
                    
    def process_line(self, full_input):
        try:
            sexp = self.read(full_input)
            if sexp:
                v = self.eval(sexp, report=True)
                if not v.is_nil():
                    self.emit(str(v))
        except LispError as e:
            self.emit_error(e)

    def emit(self, s):
        print(s)

    def emit_error(self, e):
        self.emit(';; ' + str(e))

    def emit_report(self, msg):
        self.emit(';; ' + msg)

    def repl(self, on_error=None):
        """
        A simple read-eval-print loop 
        running on the current engine
        """
        self.new_env()   # working environment
        done = False
        while not done:
            try:
                # to deal with win_unicode_console flushing problem
                full_input = ''
                pr = self._prompt
                while True:
                    print(pr + ' ', end='')
                    sys.stdout.flush()
                    s = input()  #.decode(_DEFAULT_ENCODING)
                    full_input += s + ' '
                    if self.balance(full_input):
                        break
                    pr = '.' * len(pr)   # use continuation prompt after first iteration
                self.process_line(full_input)
            except EOFError:
                done = True
            except LispQuit:
                done = True
            except Exception as e: 
                print(traceback.format_exc())
    

if __name__ == '__main__':
    Engine().repl()
