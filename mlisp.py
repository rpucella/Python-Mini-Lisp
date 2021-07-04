"""
A simple one-file LISP interpreter ready for embedding
in a Python program to provide an internal command language.
"""

import sys
import re
import functools
import traceback

class LispError(Exception):
    def __init__(self, msg, type='lisp error'):
        super(LispError, self).__init__('{}: {}'.format(type.upper(), msg))

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

    def to_list(self):
        raise LispError('Cannot convert to a python list of values: {}'.format(self))

    def _str_cdr(self):
        raise LispError('Cannot use value as list terminator: {}'.format(self))

    def display(self):
        return str(self)

    def pp(self, prefix=0, suffix='', skip_prefix=False):
        if skip_prefix:
            return str(self) + suffix
        else:
            return(' ' * prefix) + str(self) + suffix

    def type(self):
        pass

    def is_number(self):
        return self.type() == 'number'

    def is_boolean(self):
        return self.type() == 'boolean'

    def is_string(self):
        return self.type() == 'string'

    def is_symbol(self):
        return self.type() == 'symbol'

    def is_nil(self):
        return self.type() == 'nil'

    def is_empty(self):
        return self.type() == 'empty-list'
    
    def is_cons(self):
        return self.type() == 'cons-list'

    def is_function(self):
        return self.type() in('primitive', 'function')

    def is_reference(self):
        return self.type() == 'ref'

    def is_atom(self):
        return self.type() in ['number', 'primitive', 'function', 'symbol', 'string', 'boolean']

    def is_list(self):
        return self.type() in ['empty-list', 'cons-list']

    def is_dict(self):
        return self.type() in ['dict']

    def is_true(self):
        return True

    def is_equal(self, v):
        # by default, do is_eq
        return self.is_eq(v)

    def is_eq(self, v):
        # "pointer" equality
        ##self.type() == v.type() and self.value() == v.value()
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

    def type(self):
        return 'boolean'

    def value(self):
        return self._value

    def is_true(self):
        return self._value
        
    def is_eq(self, v):
        return v.is_boolean() and self.value() == v.value()


class VReference(Value):
    def __init__(self, v):
        self._value = v

    def __repr__(self):
        return 'VReference({})'.format(self._value)

    def __str__(self):
        return '#(ref {})'.format(self._value)

    def type(self):
        return 'ref'

    def value(self):
        return self._value

    def set_value(self, v):
        self._value = v

    def is_equal(self, v):
        return v.is_reference() and self.value().is_equal(v.value())


class VDict(Value):
    def __init__(self, entries):
        self._value = entries

    def __repr__(self):
        return 'VDict({})'.format(self._value)

    def __str__(self):
        entries = ['({})'.format(' '.join([ str(x) for x in v])) for v in self._value]
        return '#(dict {})'.format(' '.join(entries))

    def pp(self, prefix=0, suffix='', skip_prefix=False):
        result = ''
        if not skip_prefix:
            result += ' ' * prefix
        result += '#(dict '
        # we could sort, but we don't have a sort order on arbitrary Value...
        for i,(k, v) in enumerate(self._value):
            skip =(i == 0)
            last =(i == len(self._value) - 1)
            sub_suffix = ')))' + suffix if last else ')\n'
            result += '(' if skip else(' ' *(prefix + 7)) + '('
            if k.is_string() or k.is_symbol() or k.is_number() or k.is_boolean():
                key_text = k.pp(prefix=prefix + 8, skip_prefix=True, suffix=' ')
                result += key_text
                result += v.pp(prefix=prefix + 8 + len(key_text), skip_prefix=True, suffix=sub_suffix)
            else:
                result += k.pp(prefix=prefix + 8, skip_prefix=True, suffix='\n')
                result += v.pp(prefix=prefix + 8, suffix=sub_suffix)
        return result
        
    def type(self):
        return 'dict'

    def value(self):
        return self._value

    def is_equal(self, v):
        # TODO: fix this comparison!
        return v.is_dict() and self.value().is_equal(v.value())

    def lookup(self, v):
        for(key, value) in self._value:
            if key.is_equal(v):
                return value
        raise LispError('Cannot find key {} in dictionary'.format(v))

    def update(self, k, v):
        result = []
        for(key, value) in self._value:
            if key.is_equal(k):
                result.append((key, v))
            else:
                result.append((key, value))
        else:
            result.append((k, v))
        return VDict(result)

    def set(self, k, v):
        for(i,(key, value)) in enumerate(self._value):
            if key.is_equal(k):
                self._value[i] =(key, v)
        else:
            self._value.append((k,v))
        return VNil()
    
    
class VString(Value):
    def __init__(self, s):
        self._value = s

    def __repr__(self):
        return 'VString({})'.format(self._value)

    def __str__(self):
        return '"{}"'.format(self._value)

    def type(self):
        return 'string'

    def display(self):
        return self._value.replace('\\"', '"').replace('\\t', '\t').replace('\\n', '\n').replace('\\\\','\\')

    def value(self):
        return self._value
        
    def is_true(self):
        return not(not self._value)
        
    def is_equal(self, v):
        return v.is_string() and self.value() == v.value()
    
    
class VInteger(Value):
    def __init__(self, v):
        self._value = v

    def __repr__(self):
        return 'VInteger({})'.format(self._value)

    def __str__(self):
        return str(self._value)

    def type(self):
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

    def type(self):
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

    def to_list(self):
        return []
    
    def __str__(self):
        return '()'

    def _str_cdr(self):
        return ')'

    def type(self):
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

    def to_list(self):
        curr = self
        result = []
        while curr.type() == 'cons-list':
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
    
    def type(self):
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

    def type(self):
        return 'primitive'

    def value(self):
        return self._primitive

    def apply(self, values):
        if len(values) < self._min:
            raise LispWrongArgNoError('Too few arguments {} to primitive {}'.format(len(values), self._name))
        if self._max and len(values) > self._max:
            raise LispWrongArgNoError('Too many arguments {} to primitive {}'.format(len(values), self._name))
        result = self._primitive(values)
        return(result or VNil())
    
    
class VSymbol(Value):
    def __init__(self, sym):
        self._symbol = canonical(sym)

    def __repr__(self):
        return 'VSymbol({})'.format(self._symbol)

    def __str__(self):
        return self._symbol

    def type(self):
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

    def type(self):
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
        return VInteger(self._value)

    
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
        return self._sexpr.as_value()


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


class SExpression:
    def is_atom(self):
        return False

    def is_cons(self):
        return False

    def is_empty(self):
        return False

    @staticmethod
    def from_value(v):
        if v.is_atom():
            return SAtom(str(v))
        if v.is_empty():
            return SEmpty()
        if v.is_cons():
            return SCons(SExpression.from_value(v.car()), SExpression.from_value(v.cdr()))
        raise LispError('Cannot convert {} back to s-expression'.format(repr(v)))
    
    
class SAtom(SExpression):
    def __init__(self, s):
        self._content = s

    def is_atom(self):
        return True

    def content(self):
        return self._content

    def __repr__(self):
        return 'SAtom({})'.format(self._content)

    def __str__(self):
        return str(self._content)

    def _str_cdr(self):
        return ' . {})'.format(self._content)

    def match_token(self, tok):
        tok = canonical(tok)
        s = canonical(self._content)
        m = re.match('^{}$'.format(tok), s)
        if m:
            return m.group()
        return None

    def as_value(self):
        content = self._content
        if content[0] == '"' and content[-1] == '"':
            return VString(content[1:-1])
        if self.match_token(r'-?[0-9]+'):
            return VInteger(int(content))
        if self.match_token(r'#t'):
            return VBoolean(True)
        if self.match_token(r'#f'):
            return VBoolean(False)
        return VSymbol(content)

    def to_expression(self): 
        content = self._content
        if content[0] == '"' and content[-1] == '"':
            return String(content[1:-1])
        if self.match_token(r'-?[0-9]+'):
            return Integer(int(content))
        if self.match_token(r'#t'):
            return Boolean(True)
        if self.match_token(r'#f'):
            return Boolean(False)
        return Symbol(content)
   
    
class SCons(SExpression):
    def __init__(self, car, cdr):
        self._car = car
        self._cdr = cdr

    def is_cons(self):
        return True

    def content(self):
        return(self._car, self._cdr)

    def __repr__(self):
        return 'SCons({}, {})'.format(repr(self._car), repr(self._cdr))

    def __str__(self):
        return '({}{}'.format(self._car, self._cdr._str_cdr())

    def _str_cdr(self):
        return ' {}{}'.format(self._car, self._cdr._str_cdr())

    def as_value(self):
        return VCons(self._car.as_value(), self._cdr.as_value())
            

class SEmpty(SExpression):
    def __repr__(self):
        return 'SEmpty()'

    def is_empty(self):
        return True

    def content(self):
        return None
    
    def __str__(self):
        return '()'

    def _str_cdr(self):
        return ')'

    def as_value(self):
        return VEmpty()



# PARSER COMBINATORS

# a parser is a function String -> Option('a, String)

def parse_sexp_wrap(p, f):
    def parser(s):
        result = p(s)
        if not result:
            return None
        return(f(result[0]), result[1])
    return parser


def parse_token(token):
    def parser(s):
        ss = s.strip()
        m = re.match(token, ss)
        if m:
            return(m.group(), ss[m.end():])
        return None
    return parser


def parse_success(v):
    def parser(s):
        return(v, s)
    return parser



# SEXPRESSIONS parser
    
def parse_lparen(s):
    return parse_token(r'\(')(s)

def parse_rparen(s):
    return parse_token(r'\)')(s)

def parse_dot(s):
    return parse_token(r'\.')(s)

def parse_atom(s):
    p = parse_token(r"[^'()#\s]+")
    return parse_sexp_wrap(p, lambda x: SAtom(x))(s)

def parse_string(s):
    def clean(s):
        return s.replace('\\"', '"').replace('\\\\', '\\')
    # p = parse_token(r'"[^"]*"')
    p = parse_token(r'"(?:[^"\\]|\\.)*"')
    return parse_sexp_wrap(p, lambda x: SAtom(x))(s)

def parse_boolean(s):
    p = parse_token(r'#(?:t|f|T|F)')
    return parse_sexp_wrap(p, lambda x: SAtom(x))(s)

def parse_sexp(s):
    p = parse_first([parse_string,
                     parse_atom,
                     parse_boolean,
                     parse_sexp_wrap(parse_seq([parse_token(r"'"),
                                                parse_sexp]),
                                lambda x: SCons(SAtom('quote'), SCons(x[1], SEmpty()))),
                                          ##parse_sexp_string,
                     parse_sexp_wrap(parse_seq([parse_lparen,
                                           parse_sexps,
                                           parse_rparen]),
                                lambda x: x[1])])
    return p(s)
    
def parse_sexps(s):
    p = parse_first([parse_sexp_wrap(parse_seq([parse_sexp,
                                           parse_sexps]),
                                lambda x: SCons(x[0], x[1])),
                     parse_success(SEmpty())])
    return p(s)

    

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


class Parser:
    def __init__(self):
        self._macros = {}
        self._gensym_count = 0

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
            return s.to_expression()
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
                    (car, cdr) = current.content()
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
                (car, cdr) = current.content()
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
            (car, cdr) = s.content()
            e = p(car)
            if e is None:
                return None
            acc = [e]
            current = cdr
            while current.is_cons():
                (car, cdr) = current.content()
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
            if s.is_atom() and canonical(s.content()) == canonical(kw):
                return canonical(kw)
            return None

        return parser


    def parse_identifier(self, s):

        identifier = r'[A-Za-z0-9-+/*_:.?!@$]*[A-Za-z-+/*_:.?!@$#][A-Za-z0-9-+/*_:.?!@$]*'

        if not s:
            return None
        if s.is_atom():
            m = s.match_token(identifier)
            return m
        return None


    def parse_exp(self, s):

        p = parse_first([self.parse_atom,
                         self.parse_quote,
                         self.parse_if,
                         self.parse_lambda,
                         self.parse_do,
                         self.parse_letrec,
                         self.parse_builtin_macros,
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
        p1 = self.parse_list([self.parse_keyword('def'),
                              self.parse_list([self.parse_identifier],
                                              tail=self.parse_rep(self.parse_identifier))],
                             tail=self.parse_exps)
        p1 = parse_wrap(p1, lambda x:(x[0][1][0][0], x[0][1][1], Do(x[1])))
        p2 = self.parse_list([self.parse_keyword('defun'),
                              self.parse_identifier,
                              self.parse_rep(self.parse_identifier)],
                             tail=self.parse_exps)
        p2 = parse_wrap(p2, lambda x:(x[0][1], x[0][2], Do(x[1])))
        p = parse_first([p1, p2])
        return p(s)


    ############################################################
    #
    # Built-in macros
    #

    def parse_builtin_macros(self, s):
        p = parse_first([self.parse_let,
                         self.parse_letstar,
                         self.parse_loop,
                         self.parse_funrec,
                         self.parse_dict,
                         self.parse_and,
                         self.parse_or])
        return p(s)
    
    def parse_binding(self, s):
        p = self.parse_list([self.parse_identifier,
                        self.parse_exp])
        p = parse_wrap(p, lambda x:(x[0], x[1]))
        return p(s)

    def parse_let(self, s):
        p = self.parse_list([self.parse_keyword('let'),
                             self.parse_rep(self.parse_binding)],
                       tail=self.parse_exps)
        p = parse_wrap(p, lambda x: self.mk_Let(x[0][1], Do(x[1])))
        return p(s)

    def parse_loop(self, s):
        p = self.parse_list([self.parse_keyword('loop'),
                             self.parse_identifier,
                             self.parse_rep(self.parse_binding)],
                       tail=self.parse_exps)
        p = parse_wrap(p, lambda x: self.mk_Loop(x[0][1], x[0][2], Do(x[1])))
        return p(s)
    
    def parse_funrec(self, s):
        p = self.parse_list([self.parse_keyword('funrec'),
                             self.parse_identifier,
                             self.parse_rep(self.parse_identifier)],
                            tail=self.parse_exps)
        p = parse_wrap(p, lambda x: self.mk_FunRec(x[0][1], x[0][2], Do(x[1])))
        return p(s)
    
    def parse_letstar(self, s):
        p = self.parse_list([self.parse_keyword('let*'),
                             self.parse_rep(self.parse_binding)],
                            tail=self.parse_exps)
        p = parse_wrap(p, lambda x: self.mk_LetStar(x[0][1], Do(x[1])))
        return p(s)

    def parse_exp_pair(self, s):
        p = self.parse_list([self.parse_exp,
                             self.parse_exp])
        p = parse_wrap(p, lambda x:(x[0], x[1]))
        return p(s)
 
    def parse_dict(self, s):
        p = self.parse_list([self.parse_keyword('dict')],
                            tail=self.parse_rep(self.parse_exp_pair))
        p = parse_wrap(p, lambda x: self.mk_Dict(x[1]))
        return p(s)
    
    def parse_and(self, s):
        p = self.parse_list([self.parse_keyword('and')],
                            tail=self.parse_exps)
        p = parse_wrap(p, lambda x: self.mk_And(x[1]))
        return p(s)

    def parse_or(self, s):
        p = self.parse_list([self.parse_keyword('or')],
                            tail=self.parse_exps)
        p = parse_wrap(p, lambda x: self.mk_Or(x[1]))
        return p(s)


    def mk_Let(self, bindings, body):
        params = [ id for(id, _) in bindings ]
        args = [ e for(_, e) in bindings ]
        return Apply(Lambda(params, body), args)

    def mk_LetStar(self, bindings, body):
        result = body
        for(id, e) in reversed(bindings):
            result = Apply(Lambda([id], result), [e])
        return result

    def mk_And(self, exps):
        if exps:
            result = exps[-1]
            for e in reversed(exps[:-1]):
                n = self.gensym()
                result = self.mk_Let([(n, e)], If(Symbol(n), result, Symbol(n)))
            return result
        return Boolean(True)

    def mk_Or(self, exps):
        if exps:
            result = exps[-1]
            for e in reversed(exps[:-1]):
                n = self.gensym()
                result = self.mk_Let([(n, e)], If(Symbol(n), Symbol(n), result))
            return result
        return Boolean(False)

    def mk_Dict(self, exps):
        exps = [Apply(Symbol('list'), [x, y]) for(x, y) in exps]
        return Apply(Symbol('make-dict'), [Apply(Symbol('list'), exps)])

    def mk_Loop(self, name, bindings, body):
        return Apply(LetRec([(name, Lambda([ n for(n, e) in bindings ], body))],
                            Symbol(name)),
                     [ e for(n, e) in bindings ])

    def mk_FunRec(self, name, params, body):
        return LetRec([(name, Lambda(params, body))], Symbol(name))


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
def prim_type(args):
    return VSymbol(args[0].type())


@primitive('+', 0)
def prim_plus(args):
    v = 0
    for arg in args:
        check_arg_type('+', arg, lambda v:v.is_number())
        v += arg.value()
    return VInteger(v)

@primitive('*', 0)
def prim_times(args):
    v = 1
    for arg in args:
        check_arg_type('*', arg, lambda v:v.is_number())
        v *= arg.value()
    return VInteger(v)

@primitive('-', 1)
def prim_minus(args):
    check_arg_type('-', args[0], lambda v:v.is_number())
    v = args[0].value()
    if args[1:]:
        for arg in args[1:]:
            check_arg_type('-', arg, lambda v:v.is_number())
            v -= arg.value()
        return VInteger(v)
    else:
        return VInteger(-v)

def _num_predicate(arg1, arg2, sym, pred):
    check_arg_type(sym, arg1, lambda v:v.is_number())
    check_arg_type(sym, arg2, lambda v:v.is_number())
    return VBoolean(pred(arg1.value(), arg2.value()))
    
@primitive('=', 2, 2)
def prim_numequal(args):
    return _num_predicate(args[0], args[1], '=', lambda v1, v2: v1 == v2)

@primitive('<', 2, 2)
def prim_numless(args):
    return _num_predicate(args[0], args[1], '<', lambda v1, v2: v1 < v2)

@primitive('<=', 2, 2)
def prim_numlesseq(args):
    return _num_predicate(args[0], args[1], '<=', lambda v1, v2: v1 <= v2)

@primitive('>', 2, 2)
def prim_numgreater(args):
    return _num_predicate(args[0], args[1], '>', lambda v1, v2: v1 > v2)

@primitive('>=', 2, 2)
def prim_numgreatereq(args):
    return _num_predicate(args[0], args[1], '>=', lambda v1, v2: v1 >= v2)

@primitive('not', 1, 1)
def prim_not(args):
    return VBoolean(not args[0].is_true())

@primitive('string-append', 0)
def prim_string_append(args):
    v = ''
    for arg in args:
        check_arg_type('string-append', arg, lambda v:v.is_string())
        v += arg.value()
    return VString(v)

@primitive('string-length', 1, 1)
def prim_string_length(args):
    check_arg_type('string-length', args[0], lambda v:v.is_string())
    return VInteger(len(args[0].value()))

@primitive('string-lower', 1, 1)
def prim_string_lower(args):
    check_arg_type('string-lower', args[0], lambda v:v.is_string())
    return VString(args[0].value().lower())

@primitive('string-upper', 1, 1)
def prim_string_upper(args):
    check_arg_type('string-upper', args[0], lambda v:v.is_string())
    return VString(args[0].value().upper())

@primitive('string-substring', 1, 3)
def prim_string_substring(args):
    check_arg_type('string-substring', args[0], lambda v:v.is_string())
    if len(args) > 2:
        check_arg_type('string-substring', args[2], lambda v:v.is_number())
        end = args[2].value()
    else:
        end = len(args[0].value())
    if len(args) > 1:
        check_arg_type('string-substring', args[1], lambda v:v.is_number())
        start = args[1].value()
    else:
        start = 0
    return VString(args[0].value()[start:end])

@primitive('apply', 2, 2)
def prim_apply(args):
    check_arg_type('apply', args[0], lambda v:v.is_function())
    check_arg_type('apply', args[1], lambda v:v.is_list())
    return args[0].apply(args[1].to_list())
    
@primitive('cons', 2, 2)
def prim_cons(args):
    check_arg_type('cons', args[1], lambda v:v.is_list())
    return VCons(args[0], args[1])

@primitive('append', 0)
def prim_append(args):
    v = VEmpty()
    for arg in reversed(args):
        check_arg_type('append', arg, lambda v:v.is_list())
        curr = arg
        temp = []
        while not curr.is_empty():
            temp.append(curr.car())
            curr = curr.cdr()
        for t in reversed(temp):
            v = VCons(t, v)
    return v

@primitive('reverse', 1, 1)
def prim_reverse(args):
    check_arg_type('reverse', args[0], lambda v:v.is_list())
    v = VEmpty()
    curr = args[0]
    while not curr.is_empty():
        v = VCons(curr.car(), v)
        curr = curr.cdr()
    return v

@primitive('first', 1, 1)
def prim_first(args):
    check_arg_type('first', args[0], lambda v:v.is_cons())
    return args[0].car()

@primitive('rest', 1, 1)
def prim_rest(args):
    check_arg_type('rest', args[0], lambda v:v.is_cons())
    return args[0].cdr()

@primitive('list', 0)
def prim_list(args):
    v = VEmpty()
    for arg in reversed(args):
        v = VCons(arg, v)
    return v

@primitive('length', 1, 1)
def prim_length(args):
    check_arg_type('length', args[0], lambda v:v.is_list())
    count = 0
    curr = args[0]
    while not curr.is_empty():
        count += 1
        curr = curr.cdr()
    return VInteger(count)

@primitive('nth', 2, 2)
def prim_nth(args):
    check_arg_type('nth', args[0], lambda v:v.is_list())
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
def prim_map(args):
    check_arg_type('map', args[0], lambda v:v.is_function())
    for arg in args[1:]:
        check_arg_type('map', arg, lambda v:v.is_list())
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
def prim_filter(args):
    check_arg_type('filter', args[0], lambda v:v.is_function())
    check_arg_type('filter', args[1], lambda v:v.is_list())
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
def prim_foldr(args):
    check_arg_type('foldr', args[0], lambda v:v.is_function())
    check_arg_type('foldr', args[1], lambda v:v.is_list())
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
def prim_foldl(args):
    check_arg_type('foldl', args[0], lambda v:v.is_function())
    check_arg_type('foldl', args[2], lambda v:v.is_list())
    curr = args[2]
    v = args[1]
    while not curr.is_empty():
        v = args[0].apply([v, curr.car()])
        curr = curr.cdr()
    return v

@primitive('eq?', 2, 2)
def prim_eqp(args):
    return VBoolean(args[0].is_eq(args[1]))

@primitive('eql?', 2, 2)
def prim_eqlp(args):
    return VBoolean(args[0].is_equal(args[1]))

@primitive('empty?', 1, 1)
def prim_emptyp(args):
    return VBoolean(args[0].is_empty())
    
@primitive('cons?', 1, 1)
def prim_consp(args):
    return VBoolean(args[0].is_cons())

@primitive('list?', 1, 1)
def prim_listp(args):
    return VBoolean(args[0].is_list())

@primitive('number?', 1, 1)
def prim_numberp(args):
    return VBoolean(args[0].is_number())

@primitive('boolean?', 1, 1)
def prim_booleanp(args):
    return VBoolean(args[0].is_boolean())

@primitive('string?', 1, 1)
def prim_stringp(args):
    return VBoolean(args[0].is_string())

@primitive('symbol?', 1, 1)
def prim_symbolp(args):
    return VBoolean(args[0].is_symbol())

@primitive('function?', 1, 1)
def prim_functionp(args):
    return VBoolean(args[0].is_function())

@primitive('nil?', 1, 1)
def prim_nilp(args):
    return VBoolean(args[0].is_nil())


@primitive('ref?', 1, 1)
def prim_refp(args):
    return VBoolean(args[0].is_reference())

@primitive('ref', 1, 1)
def prim_ref(args):
    return VReference(args[0])

@primitive('ref-get', 1, 1)
def prim_ref_get(args):
    check_arg_type('ref-get', args[0], lambda v: v.is_reference())
    return args[0].value()

@primitive('ref-set', 2, 2)
def prim_ref_set(args):
    check_arg_type('ref-set', args[0], lambda v: v.is_reference())
    args[0].set_value(args[1])
    return VNil()


@primitive('dict?', 1, 1)
def prim_dictp(args):
    return VBoolean(args[0].is_dict())
    
@primitive('make-dict', 1, 1)
def prim_make_dict(args):
    check_arg_type('make-dict', args[0], lambda v:v.is_list())
    entries = [ tuple(v.to_list()) for v in args[0].to_list() ]
    for entry in entries:
        if len(entry) != 2:
            raise LispError('Wrong number of element in entry {}'.format(entry))
    return VDict(entries)

@primitive('get', 2, 2)
def prim_dict_get(args):
    check_arg_type('get', args[0], lambda v:v.is_dict())
    check_arg_type('get', args[1], lambda v:v.is_atom())
    return args[0].lookup(args[1])

@primitive('update', 3, 3)
def prim_dict_update(args):
    check_arg_type('update', args[0], lambda v:v.is_dict())
    check_arg_type('update', args[1], lambda v:v.is_atom())
    return args[0].update(args[1], args[2])

@primitive('set', 3, 3)
def prim_dict_set(args):
    check_arg_type('set', args[0], lambda v:v.is_dict())
    check_arg_type('set', args[1], lambda v:v.is_atom())
    return args[0].set(args[1], args[2])


class Engine:
    def __init__(self, prompt='>', bindings=None):
        # basic environment
        self._env = Environment(bindings=_PRIMITIVES)
        self._env.add('empty', VEmpty())
        self._env.add('nil', VNil())
        self._env.add('print', VPrimitive('print', self.prim_print, 0, None))
        if bindings:
            self.add_env(bindings)
        self._parser = Parser()
        self._prompt= prompt

    def prompt(self):
        return self._prompt + ' '

    def cont_prompt(self):
        return '.' * len(self._prompt) + ' '

    def set_prompt(self, prompt):
        self._prompt = prompt
        return self

    def add_env(self, bindings):
        self._env = Environment(bindings=bindings, previous=self._env)
        return self

    def prim_print(self, args):
        result = ' '.join([arg.display() for arg in args])
        self.emit_string(result)

    def read(self, s):
        if not s.strip():
            return None
        result = parse_sexp(s)
        if result:
            return result[0]
        raise LispReadError('Cannot read {}'.format(s))
        
    def eval(self, s):
        sexp = self.read(s)
        return self.eval_sexp(sexp)

    def eval_sexp(self, sexp, report=False):
        (type, result) = self._parser.parse(sexp)
        if type == 'define':
            (name, expr) = result
            name = canonical(name)
            v = expr.eval(self._env)
            self._env.add(name, v)
            if report:
                ##print(';; {}'.format(name))
                self.emit_report(name)
            return VNil()
        if type == 'defun':
            (name, params, expr) = result
            params = [ canonical(p) for p in params ]
            v = VFunction(params, expr, self._env)
            self._env.add(name, v)
            if report:
                ##print(';; {}'.format(name))
                self.emit_report(name)
            return VNil()
        if type == 'exp':
            return result.eval(self._env)
        raise LispError('Cannot recognize top level type {}'.format(type))

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
                v = self.eval_sexp(sexp, report=True)
                self.emit_result(v)
        except LispError as e:
            self.emit_error(e)

    def emit_string(self, s):
        print(s)

    def emit_error(self, e):
        self.emit_string(';; ' + str(e))

    def emit_report(self, msg):
        self.emit_string(';; ' + msg)

    def emit_result(self, v):
        if not v.is_nil():
            self.emit_string(v.pp())

            
    def repl(self, on_error=None):
        """
        A simple read-eval-print loop 
        running on the current engine
        """
        self.add_env([])   # add working environment
        done = False
        while not done:
            try:
                # to deal with win_unicode_console flushing problem
                full_input = ''
                pr = self.prompt()
                while True:
                    print(pr, end='')
                    sys.stdout.flush()
                    s = input()  #.decode(_DEFAULT_ENCODING)
                    full_input += s + ' '
                    if self.balance(full_input):
                        break
                    pr = self.cont_prompt()   # use continuation prompt after first iteration
                self.process_line(full_input)
            except EOFError:
                done = True
            except LispQuit:
                done = True
            except Exception as e: 
                print(traceback.format_exc())
    

if __name__ == '__main__':
    Engine().repl()
