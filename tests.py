from unittest import TestCase

import mlisp


# TODO - share testing function between the various pieces that have commonality
#  e.g., parse_sexp_int <- used to test both parse_sexp() and to test engine.read()

def _make_list (struct):
    if type(struct) == type([]):
        result = mlisp.VEmpty()
        for r in reversed(struct):
            result = mlisp.VCons(_make_list(r), result)
        return result
    else:
        return struct

    
def _unmake_list (lst):
    if lst.is_list():
        current = lst
        result = []
        while current.is_cons():
            result.append(_unmake_list(current.car()))
            current = current.cdr()
        return result
    else:
        return lst


class TestEnvironment(TestCase):

    def test_add_lookup(self):
        # basic add + lookup
        e = mlisp.Environment()
        e.add('Alice', 42)
        self.assertEqual(e.lookup('alice'), 42)
        self.assertEqual(e.lookup('ALICE'), 42)
        self.assertEqual(list(e.bindings()), [('alice',42)], 'bindings')
        self.assertEqual(e.previous(), None)

    def test_initial(self):
        # initial bindings
        e = mlisp.Environment(bindings=[('Alice', 42), ('Bob', 84)])
        self.assertEqual(e.lookup('ALICE'), 42)
        self.assertEqual(e.lookup('BOB'), 84)
        self.assertEqual(list(e.bindings()), [('alice',42), ('bob', 84)])
        self.assertEqual(e.previous(), None)

    def test_linked(self):
        # linked environments
        e = mlisp.Environment(bindings=[('alice', 42)])
        e2 = mlisp.Environment(bindings=[('bob', 84)], previous=e)
        self.assertEqual(e2.lookup('alice'), 42)
        self.assertEqual(e2.lookup('bob'), 84)
        self.assertEqual(e2.previous(), e)

    def test_overwrites(self):
        # add overwrites existing
        e = mlisp.Environment(bindings=[('Alice', 42)])
        e.add('Alice', 84)
        self.assertEqual(list(e.bindings()), [('alice', 84)])
        e2 = mlisp.Environment(previous=e)
        e2.add('Alice', 42)
        self.assertEqual(list(e2.bindings()), [('alice', 42)])
        self.assertEqual(list(e2.previous().bindings()), [('alice', 84)])

    def test_updates(self):
        # updates
        e = mlisp.Environment(bindings=[('Alice', 42), ('Bob', 84)])
        e.update('Alice', 168)
        self.assertEqual(list(e.bindings()), [('alice', 168), ('bob', 84)])
        e = mlisp.Environment(bindings=[('Alice', 42)])
        e2 = mlisp.Environment(bindings=[('Bob', 84)], previous=e)
        e2.update('Alice', 168)
        self.assertEqual(list(e2.bindings()), [('bob', 84)])
        self.assertEqual(list(e2.previous().bindings()), [('alice', 168)])


class TestValueBoolean(TestCase):

    def test_true(self):
        # True
        b = mlisp.VBoolean(True)
        self.assertEqual(str(b), '#true')
        self.assertEqual(b.display(), '#true')
        self.assertEqual(b.kind(), 'boolean')
        self.assertEqual(b.is_number(), False)
        self.assertEqual(b.is_boolean(), True)
        self.assertEqual(b.is_string(), False)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_empty(), False)
        self.assertEqual(b.is_cons(), False)
        self.assertEqual(b.is_function(), False)
        self.assertEqual(b.is_atom(), True)
        self.assertEqual(b.is_list(), False)
        self.assertEqual(b.is_true(), True)
        self.assertEqual(b.is_equal(mlisp.VBoolean(True)), True)
        self.assertEqual(b.is_equal(mlisp.VBoolean(False)), False)
        self.assertEqual(b.is_equal(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_eq(mlisp.VBoolean(True)), True)
        self.assertEqual(b.is_eq(mlisp.VBoolean(False)), False)
        self.assertEqual(b.is_eq(mlisp.VNumber(42)), False)
        self.assertEqual(b.value(), True)

    def test_false(self):
        b = mlisp.VBoolean(False)
        self.assertEqual(str(b), '#false')
        self.assertEqual(b.display(), '#false')
        self.assertEqual(b.kind(), 'boolean')
        self.assertEqual(b.is_number(), False)
        self.assertEqual(b.is_boolean(), True)
        self.assertEqual(b.is_string(), False)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_empty(), False)
        self.assertEqual(b.is_cons(), False)
        self.assertEqual(b.is_function(), False)
        self.assertEqual(b.is_atom(), True)
        self.assertEqual(b.is_list(), False)
        self.assertEqual(b.is_true(), False)
        self.assertEqual(b.is_equal(mlisp.VBoolean(True)), False)
        self.assertEqual(b.is_equal(mlisp.VBoolean(False)), True)
        self.assertEqual(b.is_equal(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_eq(mlisp.VBoolean(True)), False)
        self.assertEqual(b.is_eq(mlisp.VBoolean(False)), True)
        self.assertEqual(b.is_eq(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertEqual(b.value(), False)
    

class TestValueString(TestCase):
    
    def test_empty(self):
        # empty
        b = mlisp.VString('')
        self.assertEqual(str(b), '""')
        self.assertEqual(b.display(), '')
        self.assertEqual(b.kind(), 'string')
        self.assertEqual(b.is_number(), False)
        self.assertEqual(b.is_boolean(), False)
        self.assertEqual(b.is_string(), True)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_empty(), False)
        self.assertEqual(b.is_cons(), False)
        self.assertEqual(b.is_function(), False)
        self.assertEqual(b.is_atom(), True)
        self.assertEqual(b.is_list(), False)
        self.assertEqual(b.is_true(), False)
        self.assertEqual(b.is_equal(mlisp.VString('')), True)
        self.assertEqual(b.is_equal(mlisp.VString('Alice')), False)
        self.assertEqual(b.is_equal(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_eq(mlisp.VString('')), False)
        self.assertEqual(b.is_eq(mlisp.VString('Alice')), False)
        self.assertEqual(b.is_eq(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertEqual(b.value(), '')

    def test_non_empty(self):
        # non-empty
        b = mlisp.VString('Alice')
        self.assertEqual(str(b), '"Alice"')
        self.assertEqual(b.display(), 'Alice')
        self.assertEqual(b.kind(), 'string')
        self.assertEqual(b.is_number(), False)
        self.assertEqual(b.is_boolean(), False)
        self.assertEqual(b.is_string(), True)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_empty(), False)
        self.assertEqual(b.is_cons(), False)
        self.assertEqual(b.is_function(), False)
        self.assertEqual(b.is_atom(), True)
        self.assertEqual(b.is_list(), False)
        self.assertEqual(b.is_true(), True)
        self.assertEqual(b.is_equal(mlisp.VString('')), False)
        self.assertEqual(b.is_equal(mlisp.VString('Alice')), True)
        self.assertEqual(b.is_equal(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_eq(mlisp.VString('')), False)
        self.assertEqual(b.is_eq(mlisp.VString('Alice')), False)
        self.assertEqual(b.is_eq(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertEqual(b.value(), 'Alice')

    def test_special(self):
        # special characters
        b = mlisp.VString('\\t\\n\\"')
        self.assertEqual(str(b), '"\\t\\n\\""')
        self.assertEqual(b.display(), '\t\n"')
        # accented characters
        b = mlisp.VString('\u00e9\u00ea\00e8')
        self.assertEqual(str(b), '"\u00e9\u00ea\00e8"')
        self.assertEqual(b.display(), '\u00e9\u00ea\00e8')


class TestValueInteger(TestCase):

    def test_zero(self):
        # zero
        b = mlisp.VNumber(0)
        self.assertEqual(str(b), '0')
        self.assertEqual(b.display(), '0')
        self.assertEqual(b.kind(), 'number')
        self.assertEqual(b.is_number(), True)
        self.assertEqual(b.is_boolean(), False)
        self.assertEqual(b.is_string(), False)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_empty(), False)
        self.assertEqual(b.is_cons(), False)
        self.assertEqual(b.is_function(), False)
        self.assertEqual(b.is_atom(), True)
        self.assertEqual(b.is_list(), False)
        self.assertEqual(b.is_true(), False)
        self.assertEqual(b.is_equal(mlisp.VNumber(0)), True)
        self.assertEqual(b.is_equal(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_equal(mlisp.VString('Alice')), False)
        self.assertEqual(b.is_eq(mlisp.VNumber(0)), True)
        self.assertEqual(b.is_eq(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_eq(mlisp.VString('Alice')), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertEqual(b.value(), 0)

    def test_non_zero(self):
        # non-zero
        b = mlisp.VNumber(42)
        self.assertEqual(str(b), '42')
        self.assertEqual(b.display(), '42')
        self.assertEqual(b.kind(), 'number')
        self.assertEqual(b.is_number(), True)
        self.assertEqual(b.is_boolean(), False)
        self.assertEqual(b.is_string(), False)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_empty(), False)
        self.assertEqual(b.is_cons(), False)
        self.assertEqual(b.is_function(), False)
        self.assertEqual(b.is_atom(), True)
        self.assertEqual(b.is_list(), False)
        self.assertEqual(b.is_true(), True)
        self.assertEqual(b.is_equal(mlisp.VNumber(0)), False)
        self.assertEqual(b.is_equal(mlisp.VNumber(42)), True)
        self.assertEqual(b.is_equal(mlisp.VString('Alice')), False)
        self.assertEqual(b.is_eq(mlisp.VNumber(0)), False)
        self.assertEqual(b.is_eq(mlisp.VNumber(42)), True)
        self.assertEqual(b.is_eq(mlisp.VString('Alice')), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertEqual(b.value(), 42)


class TestValueNil(TestCase):

    def test_nil(self):
        b = mlisp.VNil()
        self.assertEqual(str(b), '#nil')
        self.assertEqual(b.display(), '#nil')
        self.assertEqual(b.kind(), 'nil')
        self.assertEqual(b.is_number(), False)
        self.assertEqual(b.is_boolean(), False)
        self.assertEqual(b.is_string(), False)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), True)
        self.assertEqual(b.is_empty(), False)
        self.assertEqual(b.is_cons(), False)
        self.assertEqual(b.is_function(), False)
        self.assertEqual(b.is_atom(), False)
        self.assertEqual(b.is_list(), False)
        self.assertEqual(b.is_true(), False)
        self.assertEqual(b.is_equal(mlisp.VNil()), True)
        self.assertEqual(b.is_equal(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_eq(mlisp.VNil()), True)
        self.assertEqual(b.is_eq(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertIs(b.value(), None)


class TestValueEmpty(TestCase):
    
    def test_empty(self):
        b = mlisp.VEmpty()
        self.assertEqual(str(b), '()')
        self.assertEqual(b.display(), '()')
        self.assertEqual(b.kind(), 'empty-list')
        self.assertEqual(b.is_number(), False)
        self.assertEqual(b.is_boolean(), False)
        self.assertEqual(b.is_string(), False)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_empty(), True)
        self.assertEqual(b.is_cons(), False)
        self.assertEqual(b.is_function(), False)
        self.assertEqual(b.is_atom(), False)
        self.assertEqual(b.is_list(), True)
        self.assertEqual(b.is_true(), False)
        self.assertEqual(b.is_equal(mlisp.VEmpty()), True)
        self.assertEqual(b.is_equal(mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())), False)
        self.assertEqual(b.is_equal(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_eq(mlisp.VEmpty()), True)
        self.assertEqual(b.is_eq(mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())), False)
        self.assertEqual(b.is_eq(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertEqual(b.value() is None, True)
        self.assertEqual(b.to_list(), [])


class TestValueCons(TestCase):
    
    def test_cons_1(self):
        car = mlisp.VNumber(42)
        cdr = mlisp.VEmpty()
        b = mlisp.VCons(car, cdr)
        self.assertEqual(str(b), '(42)')
        self.assertEqual(b.display(), '(42)')
        self.assertEqual(b.kind(), 'cons-list')
        self.assertEqual(b.is_number(), False)
        self.assertEqual(b.is_boolean(), False)
        self.assertEqual(b.is_string(), False)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_empty(), False)
        self.assertEqual(b.is_cons(), True)
        self.assertEqual(b.is_function(), False)
        self.assertEqual(b.is_atom(), False)
        self.assertEqual(b.is_list(), True)
        self.assertEqual(b.is_true(), True)
        self.assertEqual(b.is_equal(mlisp.VEmpty()), False)
        self.assertEqual(b.is_equal(mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())), True)
        self.assertEqual(b.is_equal(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_eq(mlisp.VEmpty()), False)
        self.assertEqual(b.is_eq(mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())), False)
        self.assertEqual(b.is_eq(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertEqual(b.value(), (car, cdr))
        self.assertEqual(b.to_list(), [car])
        self.assertEqual(b.car(), car)
        self.assertEqual(b.cdr(), cdr)

    def test_cons_2(self):
        car = mlisp.VNumber(42)
        cadr = mlisp.VNumber(84)
        cddr = mlisp.VEmpty()
        c = mlisp.VCons(cadr, cddr)
        b = mlisp.VCons(car, c)
        self.assertEqual(str(b), '(42 84)')
        self.assertEqual(b.display(), '(42 84)')
        self.assertEqual(b.kind(), 'cons-list')
        self.assertEqual(b.is_number(), False)
        self.assertEqual(b.is_boolean(), False)
        self.assertEqual(b.is_string(), False)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_empty(), False)
        self.assertEqual(b.is_cons(), True)
        self.assertEqual(b.is_function(), False)
        self.assertEqual(b.is_atom(), False)
        self.assertEqual(b.is_list(), True)
        self.assertEqual(b.is_true(), True)
        self.assertEqual(b.is_equal(mlisp.VEmpty()), False)
        self.assertEqual(b.is_equal(mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())), False)
        self.assertEqual(b.is_equal(mlisp.VCons(mlisp.VNumber(42), mlisp.VCons(mlisp.VNumber(84), mlisp.VEmpty()))), True)
        self.assertEqual(b.is_equal(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_eq(mlisp.VEmpty()), False)
        self.assertEqual(b.is_eq(mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())), False)
        self.assertEqual(b.is_eq(mlisp.VCons(mlisp.VNumber(42), mlisp.VCons(mlisp.VNumber(84), mlisp.VEmpty()))), False)
        self.assertEqual(b.is_eq(mlisp.VCons(mlisp.VNumber(42), c)), False)
        self.assertEqual(b.is_eq(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertEqual(b.value(), (car, c))
        self.assertEqual(b.to_list(), [car, cadr])
        self.assertEqual(b.car(), car)
        self.assertEqual(b.cdr(), c)


class TestValuePrimitive(TestCase):
    
    def test_primitive(self):
        def prim(name, args):
            return (args[0], args[1])
        i = mlisp.VNumber(42)
        j = mlisp.VNumber(0)
        b = mlisp.VPrimitive('test', prim, 2)
        self.assertEqual(str(b).startswith('#[prim '), True)
        self.assertEqual(b.display().startswith('#[prim '), True)
        self.assertEqual(b.kind(), 'primitive')
        self.assertEqual(b.is_number(), False)
        self.assertEqual(b.is_boolean(), False)
        self.assertEqual(b.is_string(), False)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_empty(), False)
        self.assertEqual(b.is_cons(), False)
        self.assertEqual(b.is_function(), True)
        self.assertEqual(b.is_atom(), False)
        self.assertEqual(b.is_list(), False)
        self.assertEqual(b.is_true(), True)
        self.assertEqual(b.is_equal(mlisp.VPrimitive('test', prim, 2)), False)
        self.assertEqual(b.is_equal(mlisp.VPrimitive('test', lambda args: 0, 2)), False)
        self.assertEqual(b.is_equal(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_eq(mlisp.VPrimitive('test', prim, 2)), False)
        self.assertEqual(b.is_equal(mlisp.VPrimitive('test2', lambda args: 0, 2)), False)
        self.assertEqual(b.is_equal(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertEqual(b.value(), prim)
        self.assertEqual(b.apply([i, j]), (i, j))


class TestValueSymbol(TestCase):
    
    def test_symbol(self):
        b = mlisp.VSymbol('Alice')
        self.assertEqual(str(b), 'alice')
        self.assertEqual(b.display(), 'alice')
        self.assertEqual(b.kind(), 'symbol')
        self.assertEqual(b.is_number(), False)
        self.assertEqual(b.is_boolean(), False)
        self.assertEqual(b.is_string(), False)
        self.assertEqual(b.is_symbol(), True)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_empty(), False)
        self.assertEqual(b.is_cons(), False)
        self.assertEqual(b.is_function(), False)
        self.assertEqual(b.is_atom(), True)
        self.assertEqual(b.is_list(), False)
        self.assertEqual(b.is_true(), True)
        self.assertEqual(b.is_equal(mlisp.VSymbol('Alice')), True)
        self.assertEqual(b.is_equal(mlisp.VSymbol('alice')), True)
        self.assertEqual(b.is_equal(mlisp.VSymbol('Bob')), False)
        self.assertEqual(b.is_equal(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_eq(mlisp.VSymbol('Alice')), True)
        self.assertEqual(b.is_eq(mlisp.VSymbol('alice')), True)
        self.assertEqual(b.is_eq(mlisp.VSymbol('Bob')), False)
        self.assertEqual(b.is_eq(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertEqual(b.value() == 'alice', True)
        # accents
        b = mlisp.VSymbol('Test\u00c9')
        self.assertEqual(str(b), 'test\u00e9')
        self.assertEqual(b.display(), 'test\u00e9')
        self.assertEqual(b.value(), 'test\u00e9')
    

class TestValueFunction(TestCase):
    
    def test_no_args(self):
        # no arguments
        i = mlisp.Integer(42)
        e = mlisp.Environment()
        b = mlisp.VFunction([], i, e)
        self.assertEqual(str(b).startswith('#[func '), True)
        self.assertEqual(b.display().startswith('#[func '), True)
        self.assertEqual(b.kind(), 'function')
        self.assertEqual(b.is_number(), False)
        self.assertEqual(b.is_boolean(), False)
        self.assertEqual(b.is_string(), False)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_empty(), False)
        self.assertEqual(b.is_cons(), False)
        self.assertEqual(b.is_function(), True)
        self.assertEqual(b.is_atom(), False)
        self.assertEqual(b.is_list(), False)
        self.assertEqual(b.is_true(), True)
        self.assertEqual(b.is_equal(mlisp.VFunction([], mlisp.Integer(42), mlisp.Environment())), False)
        self.assertEqual(b.is_equal(mlisp.VFunction([], mlisp.Integer(84), mlisp.Environment())), False)
        self.assertEqual(b.is_equal(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_eq(mlisp.VFunction([], mlisp.Integer(42), mlisp.Environment())), False)
        self.assertEqual(b.is_eq(mlisp.VFunction([], mlisp.Integer(84), mlisp.Environment())), False)
        self.assertEqual(b.is_eq(mlisp.VNumber(42)), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertEqual(b.value(), ([], i, e))
        result = b.apply([])
        self.assertEqual(result.is_number(), True)
        self.assertEqual(result.value(), 42)

    def test_2_args(self):
        # 2 arguments
        i = mlisp.Integer(42)
        e = mlisp.Environment()
        b = mlisp.VFunction(['x', 'y'], i, e)
        self.assertEqual(b.value(), (['x', 'y'], i, e))
        result = b.apply([mlisp.VNumber(0), mlisp.VNumber(0)])
        self.assertEqual(result.is_number(), True)
        self.assertEqual(result.value(), 42)

    def test_2_args_1_used(self):
        # 2 arguments, one used
        i = mlisp.Symbol('x')
        e = mlisp.Environment()
        b = mlisp.VFunction(['x', 'y'], i, e)
        self.assertEqual(b.value(), (['x', 'y'], i, e))
        result = b.apply([mlisp.VNumber(42), mlisp.VNumber(0)])
        self.assertEqual(result.is_number(), True)
        self.assertEqual(result.value(), 42)

    def test_2_args_env(self):
        # 2 arguments, using environment
        i = mlisp.Symbol('z')
        e = mlisp.Environment(bindings=[('z', mlisp.VNumber(42))])
        b = mlisp.VFunction(['x', 'y'], i, e)
        self.assertEqual(b.value(), (['x', 'y'], i, e))
        result = b.apply([mlisp.VNumber(0), mlisp.VNumber(0)])
        self.assertEqual(result.is_number(), True)
        self.assertEqual(result.value(), 42)



#
# Expressions
#


class TestExp(TestCase):

    def test_symbol(self):
        env = mlisp.Environment(bindings=[('Alice', mlisp.VNumber(42))])
        e = mlisp.Symbol('Alice')
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        e = mlisp.Symbol('alice')
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_string(self):
        env = mlisp.Environment()
        e = mlisp.String('')
        v = e.eval(env)
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '')
        e = mlisp.String('Alice')
        v = e.eval(env)
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        # accents
        e = mlisp.String('Test\u00e9')
        v = e.eval(env)
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Test\u00e9')


    def test_integer(self):
        env = mlisp.Environment()
        e = mlisp.Integer(0)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 0)
        e = mlisp.Integer(42)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_boolean(self):
        env = mlisp.Environment()
        e = mlisp.Boolean(True)
        v = e.eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        e = mlisp.Boolean(False)
        v = e.eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_if(self):
        # then branch
        env = mlisp.Environment([('a', mlisp.VNumber(42))])
        e = mlisp.If(mlisp.Boolean(True), mlisp.Symbol('a'), mlisp.Symbol('b'))
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # else branch
        e = mlisp.If(mlisp.Boolean(False), mlisp.Symbol('b'), mlisp.Symbol('a'))
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_lambda(self):
        # simple
        env = mlisp.Environment()
        e = mlisp.Lambda(['a', 'b'], mlisp.Symbol('a'))
        v = e.eval(env)
        self.assertEqual(v.is_function(), True)
        v = v.apply([mlisp.VNumber(42), mlisp.VNumber(0)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # environment
        env = mlisp.Environment(bindings=[('c', mlisp.VNumber(42))])
        e = mlisp.Lambda(['a', 'b'], mlisp.Symbol('c'))
        v = e.eval(env)
        self.assertEqual(v.is_function(), True)
        v = v.apply([mlisp.VNumber(1), mlisp.VNumber(0)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_apply(self):
        # simple
        env = mlisp.Environment()
        f = mlisp.VFunction(['x', 'y'], mlisp.Symbol('x'), env)
        env = mlisp.Environment(bindings=[('f', f), ('a', mlisp.VNumber(42)), ('b', mlisp.VNumber(0))])
        e = mlisp.Apply(mlisp.Symbol('f'),[mlisp.Symbol('a'), mlisp.Symbol('b')])
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)

        # static vs dynamic binding
        env = mlisp.Environment(bindings=[('a', mlisp.VNumber(42))])
        f = mlisp.VFunction(['x', 'y'], mlisp.Symbol('a'), env)
        env = mlisp.Environment(bindings=[('f', f), ('a', mlisp.VNumber(84)), ('b', mlisp.VNumber(0))])
        e = mlisp.Apply(mlisp.Symbol('f'),[mlisp.Symbol('a'), mlisp.Symbol('b')])
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_quote(self):
        env = mlisp.Environment()
        # symbol
        s = mlisp.VSymbol('Alice')
        e = mlisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'alice')
        # symobl (accents)
        s = mlisp.VSymbol('TEST\u00c9')
        e = mlisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'test\u00e9')
        # string
        s = mlisp.VString('Alice')
        e = mlisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        # string (accents)
        s = mlisp.VString('Test\u00e9')
        e = mlisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Test\u00e9')
        # integer
        s = mlisp.VNumber(42)
        e = mlisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # boolean
        s = mlisp.VBoolean(True)
        e = mlisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        s = mlisp.VBoolean(False)
        e = mlisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        # empty
        s = mlisp.VEmpty()
        e = mlisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_empty(), True)
        # cons
        s = mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())
        e = mlisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_cons(), True)
        self.assertEqual(v.car().is_number(), True)
        self.assertEqual(v.car().value(), 42)
        self.assertEqual(v.cdr().is_empty(), True)
        # cons 2
        s = mlisp.VCons(mlisp.VNumber(42), mlisp.VCons(mlisp.VSymbol('Alice'), mlisp.VEmpty()))
        e = mlisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_cons(), True)
        self.assertEqual(v.car().is_number(), True)
        self.assertEqual(v.car().value(), 42)
        self.assertEqual(v.cdr().is_cons(), True)
        self.assertEqual(v.cdr().car().is_symbol(), True)
        self.assertEqual(v.cdr().car().value(), 'alice')
        self.assertEqual(v.cdr().cdr().is_empty(), True)



    # maybe use FakeExps for everything?

    def test_do(self):
        env = mlisp.Environment(bindings=[('a', mlisp.VNumber(42))])
        # empty
        e = mlisp.Do([])
        v = e.eval(env)
        self.assertEqual(v.is_nil(), True)
        # single
        e = mlisp.Do([mlisp.Symbol('a')])
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # many 
        class FakeExp:   # -- if it quacks like a duck... 
            def __init__ (self, newN):
                self.value = 0
                self.newN = newN
            def eval (self, env):
                self.value = self.newN
                return env.lookup('a')
        fe1 = FakeExp(42)
        fe2 = FakeExp(84)
        e = mlisp.Do([fe1, fe2, mlisp.Symbol('a')])
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        self.assertEqual(fe1.value, 42)
        self.assertEqual(fe2.value, 84)


    def test_letrec(self):
        env = mlisp.Environment(bindings=[('a', mlisp.VNumber(42))])
        # empty
        e = mlisp.LetRec([], mlisp.Symbol('a'))
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # many / one -> two
        e = mlisp.LetRec([('one', mlisp.Lambda(['x', 'y'], mlisp.Symbol('two'))),
                         ('two', mlisp.Lambda(['x'], mlisp.Symbol('a')))],
                        mlisp.Apply(mlisp.Symbol('one'), [mlisp.Integer(0), mlisp.Integer(0)]))                    
        v = e.eval(env)
        self.assertEqual(v.is_function(), True)
        v = v.apply([mlisp.VNumber(0)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # many / two -> one
        e = mlisp.LetRec([('one', mlisp.Lambda(['x'], mlisp.Symbol('a'))),
                         ('two', mlisp.Lambda(['x', 'y'], mlisp.Symbol('one')))],
                        mlisp.Apply(mlisp.Symbol('two'), [mlisp.Integer(0), mlisp.Integer(0)]))                    
        v = e.eval(env)
        self.assertEqual(v.is_function(), True)
        v = v.apply([mlisp.VNumber(0)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
    

#
# SExpression parsing
#

class TestSExpParsing(TestCase):
    
    def test_sexp_parse_symbol(self):
        inp = 'Alice'
        (s, rest) = mlisp.Reader().parse_sexp(inp)
        self.assertEqual(rest, '')
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.is_symbol(), True)
        self.assertEqual(s.value(), 'alice')
        # accents
        inp = 'TEST\u00c9'
        (s, rest) = mlisp.Reader().parse_sexp(inp)
        self.assertEqual(s.is_symbol(), True)
        self.assertEqual(s.value(), 'test\u00e9')


    def test_sexp_parse_string(self):
        inp = '"Alice"'
        (s, rest) = mlisp.Reader().parse_sexp(inp)
        self.assertEqual(rest, '')
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.is_string(), True)
        self.assertEqual(s.value(), 'Alice')
        # accents
        inp = '"Test\u00e9"'
        (s, rest) = mlisp.Reader().parse_sexp(inp)
        self.assertEqual(s.is_string(), True)
        self.assertEqual(s.value(), 'Test\u00e9')


    def test_sexp_parse_integer(self):
        inp = '42'
        (s, rest) = mlisp.Reader().parse_sexp(inp)
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.is_number(), True)
        self.assertEqual(s.value(), 42)


    def test_sexp_parse_boolean(self):
        inp = '#true'
        (s, rest) = mlisp.Reader().parse_sexp(inp)
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.is_boolean(), True)
        self.assertEqual(s.value(), True)
        inp = '#false'
        (s, rest) = mlisp.Reader().parse_sexp(inp)
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.is_boolean(), True)
        self.assertEqual(s.value(), False)


    def test_sexp_parse_empty(self):
        inp = '()'
        (s, rest) = mlisp.Reader().parse_sexp(inp)
        self.assertEqual(s.is_atom(), False)
        self.assertEqual(s.is_empty(), True)
        self.assertEqual(s.is_cons(), False)


    def test_sexp_parse_cons(self):
        inp = '(42 Alice Bob)'
        (s, rest) = mlisp.Reader().parse_sexp(inp)
        self.assertEqual(s.is_atom(), False)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), True)
        self.assertEqual(s.is_cons(), True)
        self.assertEqual(s.car().is_number(), True)
        self.assertEqual(s.car().value(), 42)
        self.assertEqual(s.cdr().is_cons(), True)
        self.assertEqual(s.cdr().car().is_symbol(), True)
        self.assertEqual(s.cdr().car().value(), 'alice')
        self.assertEqual(s.cdr().cdr().is_cons(), True)
        self.assertEqual(s.cdr().cdr().car().is_symbol(), True)
        self.assertEqual(s.cdr().cdr().car().value(), 'bob')
        self.assertEqual(s.cdr().cdr().cdr().is_empty(), True)


    def test_sexp_parse_cons_nested(self):
        inp = '((42 Alice) ((Bob)))'
        (s, rest) = mlisp.Reader().parse_sexp(inp)
        self.assertEqual(s.is_atom(), False)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), True)
        # (42 Alice)
        self.assertEqual(s.car().is_cons(), True)
        self.assertEqual(s.car().car().is_number(), True)
        self.assertEqual(s.car().car().value(), 42)
        self.assertEqual(s.car().cdr().is_cons(), True)
        self.assertEqual(s.car().cdr().car().is_symbol(), True)
        self.assertEqual(s.car().cdr().car().value(), 'alice')
        self.assertEqual(s.car().cdr().cdr().is_empty(), True)
        self.assertEqual(s.cdr().is_cons(), True)
        # ((Bob))
        self.assertEqual(s.cdr().car().is_cons(), True)
        self.assertEqual(s.cdr().car().car().is_cons(), True)
        self.assertEqual(s.cdr().car().car().car().is_symbol(), True)
        self.assertEqual(s.cdr().car().car().car().value(), 'bob')
        self.assertEqual(s.cdr().car().car().cdr().is_empty(), True)
        self.assertEqual(s.cdr().car().cdr().is_empty(), True)
        self.assertEqual(s.cdr().cdr().is_empty(), True)


    def test_sexp_parse_rest(self):
        inp = '42 xyz'
        (s, rest) = mlisp.Reader().parse_sexp(inp)
        self.assertEqual(rest, ' xyz')
        inp = 'Alice xyz'
        (s, rest) = mlisp.Reader().parse_sexp(inp)
        self.assertEqual(rest, ' xyz')
        inp = '"Alice" xyz'
        (s, rest) = mlisp.Reader().parse_sexp(inp)
        self.assertEqual(rest, ' xyz')
        inp = '#true xyz'
        (s, rest) = mlisp.Reader().parse_sexp(inp)
        self.assertEqual(rest, ' xyz')
        inp = '#false xyz'
        (s, rest) = mlisp.Reader().parse_sexp(inp)
        self.assertEqual(rest, ' xyz')
        inp = '() xyz'
        (s, rest) = mlisp.Reader().parse_sexp(inp)
        self.assertEqual(rest, ' xyz')
        inp = '(Alice Bob) xyz'
        (s, rest) = mlisp.Reader().parse_sexp(inp)
        self.assertEqual(rest, ' xyz')
    

    
#
# Expression parsing
#


class TestExpParsing(TestCase):

    
    def test_exp_parse_symbol(self):
        env = mlisp.Environment(bindings=[('Alice', mlisp.VNumber(42))])
        inp = _make_list(mlisp.VSymbol('Alice'))
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # accents
        env = mlisp.Environment(bindings=[('Test\u00e9', mlisp.VNumber(42))])
        inp = _make_list(mlisp.VSymbol('Test\u00e9'))
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_exp_parse_string(self):
        env = mlisp.Environment()
        inp = _make_list(mlisp.VString('Alice'))
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        # accents
        inp = _make_list(mlisp.VString('Test\u00e9'))
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Test\u00e9')


    def test_exp_parse_integer(self):
        env = mlisp.Environment()
        inp = _make_list(mlisp.VNumber(42))
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_exp_parse_boolean(self):
        env = mlisp.Environment()
        inp = _make_list(mlisp.VBoolean(True))
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        inp = _make_list(mlisp.VBoolean(False))
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_exp_parse_if(self):
        # then branch
        env = mlisp.Environment([('a', mlisp.VNumber(42))])
        inp = _make_list([mlisp.VSymbol('if'), mlisp.VBoolean(True), mlisp.VSymbol('a'), mlisp.VBoolean(False)])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # else branch
        inp = _make_list([mlisp.VSymbol('if'), mlisp.VBoolean(False), mlisp.VBoolean(False), mlisp.VSymbol('a')])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_exp_parse_lambda(self):
        # simple
        env = mlisp.Environment()
        inp = _make_list([mlisp.VSymbol('fn'), [mlisp.VSymbol('a'), mlisp.VSymbol('b')], mlisp.VSymbol('a')])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_function(), True)
        v = v.apply([mlisp.VNumber(42), mlisp.VNumber(0)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_exp_parse_apply(self):
        env = mlisp.Environment()
        f = mlisp.VFunction(['x', 'y'], mlisp.Symbol('x'), env)
        env = mlisp.Environment(bindings=[('f', f), ('a', mlisp.VNumber(42)), ('b', mlisp.VNumber(0))])
        inp = _make_list([mlisp.VSymbol('f'), mlisp.VSymbol('a'), mlisp.VSymbol('b')])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_exp_parse_quote(self):
        env = mlisp.Environment()
        # symbol
        inp = _make_list([mlisp.VSymbol('quote'), mlisp.VSymbol('Alice')])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'alice')
        # empty
        inp = _make_list([mlisp.VSymbol('quote'), []])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_empty(), True)
        # cons
        inp = _make_list([mlisp.VSymbol('quote'), [mlisp.VNumber(42)]])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_cons(), True)
        self.assertEqual(v.car().is_number(), True)
        self.assertEqual(v.car().value(), 42)
        self.assertEqual(v.cdr().is_empty(), True)


    def test_exp_parse_do(self):
        env = mlisp.Environment(bindings=[('a', mlisp.VNumber(42))])
        # empty
        inp = _make_list([mlisp.VSymbol('do')])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_nil(), True)
        # single
        inp = _make_list([mlisp.VSymbol('do'), mlisp.VSymbol('a')])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # many
        inp = _make_list([mlisp.VSymbol('do'), mlisp.VNumber(0), mlisp.VNumber(1), mlisp.VSymbol('a')])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_exp_parse_letrec(self):
        env = mlisp.Environment(bindings=[('a', mlisp.VNumber(42))])
        # empty
        inp = _make_list([mlisp.VSymbol('letrec'), [], mlisp.VSymbol('a')])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # many
        inp = _make_list([mlisp.VSymbol('letrec'), [[mlisp.VSymbol('one'), [mlisp.VSymbol('fn'), [mlisp.VSymbol('x'), mlisp.VSymbol('y')], mlisp.VSymbol('two')]],
                                     [mlisp.VSymbol('two'), [mlisp.VSymbol('fn'), [mlisp.VSymbol('x')], mlisp.VSymbol('a')]]],
                          [mlisp.VSymbol('one'), mlisp.VNumber(0), mlisp.VNumber(0)]])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_function(), True)
        v = v.apply([mlisp.VNumber(0)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)



#
# Declarations
#

class TestDeclarationParsing(TestCase):

    def test_parse_define(self):
        env = mlisp.Environment()
        inp = _make_list([mlisp.VSymbol('def'), mlisp.VSymbol('A'), mlisp.VNumber(42)])
        p = mlisp.Parser().parse_define(inp)
        self.assertEqual(type(p), type((1, 2)))
        self.assertEqual(p[0], 'a')
        v = p[1].eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)

    def test_parse_defun(self):
        env = mlisp.Environment(bindings=[('a', mlisp.VNumber(42))])
        inp = _make_list([mlisp.VSymbol('def'), [mlisp.VSymbol('FOO'), mlisp.VSymbol('A'), mlisp.VSymbol('B')], mlisp.VSymbol('a')])
        p = mlisp.Parser().parse_defun(inp)
        self.assertEqual(type(p), type((1, 2)))
        self.assertEqual(p[0], 'foo')
        self.assertEqual(p[1], ['a', 'b'])
        v = p[2].eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_parse_decl_define(self):
        env = mlisp.Environment()
        inp = _make_list([mlisp.VSymbol('def'), mlisp.VSymbol('A'), mlisp.VNumber(42)])
        r = mlisp.Parser().parse(inp)
        self.assertEqual(type(r), type((1, 2)))
        self.assertEqual(r[0], 'define')
        p = r[1]
        self.assertEqual(type(p), type((1, 2)))
        self.assertEqual(p[0], 'a')
        v = p[1].eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_parse_decl_defun(self):
        env = mlisp.Environment(bindings=[('a', mlisp.VNumber(42))])
        inp = _make_list([mlisp.VSymbol('def'), [mlisp.VSymbol('FOO'), mlisp.VSymbol('A'), mlisp.VSymbol('B')], mlisp.VSymbol('a')])
        r = mlisp.Parser().parse(inp)
        self.assertEqual(type(r), type((1, 2)))
        self.assertEqual(r[0], 'defun')
        p = r[1]
        self.assertEqual(type(p), type((1, 2)))
        self.assertEqual(p[0], 'foo')
        self.assertEqual(p[1], ['a', 'b'])
        v = p[2].eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_parse_decl_exp(self):
        env = mlisp.Environment()
        # int
        inp = _make_list(mlisp.VNumber(42))
        r = mlisp.Parser().parse(inp)
        self.assertEqual(type(r), type((1, 2)))
        self.assertEqual(r[0], 'exp')
        p = r[1]
        v = p.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # lambda
        inp = _make_list([mlisp.VSymbol('fn'), [mlisp.VSymbol('a'), mlisp.VSymbol('b')], mlisp.VSymbol('a')])
        r = mlisp.Parser().parse(inp)
        self.assertEqual(type(r), type((1, 2)))
        self.assertEqual(r[0], 'exp')
        p = r[1]
        v = p.eval(env)
        self.assertEqual(v.is_function(), True)
        v = v.apply([mlisp.VNumber(42), mlisp.VNumber(0)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


#
# Operations
#

class TestOperations(TestCase):
    
    def test_prim_type(self):
        v = mlisp.prim_type('type', [mlisp.VBoolean(True)])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'boolean')
        v = mlisp.prim_type('type', [mlisp.VString('Alice')])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'string')
        v = mlisp.prim_type('type', [mlisp.VNumber(42)])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'number')
        v = mlisp.prim_type('type', [mlisp.VNil()])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'nil')
        v = mlisp.prim_type('type', [mlisp.VEmpty()])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'empty-list')
        v = mlisp.prim_type('type', [mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'cons-list')
        def prim(name, args):
            return (args[0], args[1])
        v = mlisp.prim_type('type', [mlisp.VPrimitive('prim', prim, 2)])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'primitive')
        v = mlisp.prim_type('type', [mlisp.VSymbol('Alice')])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'symbol')
        v = mlisp.prim_type('type', [mlisp.VFunction(['a', 'b'], mlisp.Symbol('a'), mlisp.Environment())])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'function')


    def test_prim_plus(self):
        v = mlisp.prim_plus('+', [])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 0)
        v = mlisp.prim_plus('+', [mlisp.VNumber(42)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        v = mlisp.prim_plus('+', [mlisp.VNumber(42), mlisp.VNumber(84)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42 + 84)
        v = mlisp.prim_plus('+', [mlisp.VNumber(42), mlisp.VNumber(84), mlisp.VNumber(168)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42 + 84 + 168)


    def test_prim_times(self):
        v = mlisp.prim_times('*', [])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 1)
        v = mlisp.prim_times('*', [mlisp.VNumber(42)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        v = mlisp.prim_times('*', [mlisp.VNumber(42), mlisp.VNumber(84)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42 * 84)
        v = mlisp.prim_times('*', [mlisp.VNumber(42), mlisp.VNumber(84), mlisp.VNumber(168)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42 * 84 * 168)


    def test_prim_minus(self):
        v = mlisp.prim_minus('-', [mlisp.VNumber(42)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), -42)
        v = mlisp.prim_minus('-', [mlisp.VNumber(42), mlisp.VNumber(84)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42 - 84)
        v = mlisp.prim_minus('-', [mlisp.VNumber(42), mlisp.VNumber(84), mlisp.VNumber(168)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42 - 84 - 168)


    def test_prim_numequal(self):
        v = mlisp.prim_numequal('=', [mlisp.VNumber(0), mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numequal('=', [mlisp.VNumber(42), mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numequal('=', [mlisp.VNumber(0), mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_numequal('=', [mlisp.VNumber(42), mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)


    def test_prim_numless(self):
        v = mlisp.prim_numless('<', [mlisp.VNumber(0), mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_numless('<', [mlisp.VNumber(42), mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numless('<', [mlisp.VNumber(0), mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numless('<', [mlisp.VNumber(42), mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_numlesseq(self):
        v = mlisp.prim_numlesseq('<=', [mlisp.VNumber(0), mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_numlesseq('<=', [mlisp.VNumber(42), mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numlesseq('<=', [mlisp.VNumber(0), mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_numlesseq('<=', [mlisp.VNumber(42), mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)


    def test_prim_numgreater(self):
        v = mlisp.prim_numgreater('>', [mlisp.VNumber(0), mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numgreater('>', [mlisp.VNumber(42), mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_numgreater('>', [mlisp.VNumber(0), mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numgreater('>', [mlisp.VNumber(42), mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_numgreatereq(self):
        v = mlisp.prim_numgreatereq('>=', [mlisp.VNumber(0), mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numgreatereq('>=', [mlisp.VNumber(42), mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_numgreatereq('>=', [mlisp.VNumber(0), mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_numgreatereq('>=', [mlisp.VNumber(42), mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)


    def test_prim_not(self):
        v = mlisp.prim_not('not', [mlisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_not('not', [mlisp.VBoolean(False)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_not('not', [mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_not('not', [mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_not('not', [mlisp.VString('')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_not('not', [mlisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_not('not', [mlisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_not('not', [mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_string_append(self):
        v = mlisp.prim_string_append('string-append', [])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '')
        v = mlisp.prim_string_append('string-append', [mlisp.VString('Alice')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        v = mlisp.prim_string_append('string-append', [mlisp.VString('Alice'), mlisp.VString('Bob')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'AliceBob')
        v = mlisp.prim_string_append('string-append', [mlisp.VString('Alice'), mlisp.VString('Bob'), mlisp.VString('Charlie')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'AliceBobCharlie')


    def test_prim_string_length(self):
        v = mlisp.prim_string_length('string-length', [mlisp.VString('')])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 0)
        v = mlisp.prim_string_length('string-length', [mlisp.VString('Alice')])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 5)
        v = mlisp.prim_string_length('string-length', [mlisp.VString('Alice Bob')])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 9)


    def test_prim_string_lower(self):
        v = mlisp.prim_string_lower('string-lower', [mlisp.VString('')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '')
        v = mlisp.prim_string_lower('string-lower', [mlisp.VString('Alice')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'alice')
        v = mlisp.prim_string_lower('string-lower', [mlisp.VString('Alice Bob')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'alice bob')


    def test_prim_string_upper(self):
        v = mlisp.prim_string_upper('string-upper', [mlisp.VString('')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '')
        v = mlisp.prim_string_upper('string-upper', [mlisp.VString('Alice')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'ALICE')
        v = mlisp.prim_string_upper('string-upper', [mlisp.VString('Alice Bob')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'ALICE BOB')


    def test_prim_string_substring(self):
        v = mlisp.prim_string_substring('string-substring', [mlisp.VString('')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '')
        v = mlisp.prim_string_substring('string-substring', [mlisp.VString('Alice')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        v = mlisp.prim_string_substring('string-substring', [mlisp.VString('Alice'), mlisp.VNumber(0)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        v = mlisp.prim_string_substring('string-substring', [mlisp.VString('Alice'), mlisp.VNumber(1)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'lice')
        v = mlisp.prim_string_substring('string-substring', [mlisp.VString('Alice'), mlisp.VNumber(2)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'ice')
        v = mlisp.prim_string_substring('string-substring', [mlisp.VString('Alice'), mlisp.VNumber(0), mlisp.VNumber(5)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        v = mlisp.prim_string_substring('string-substring', [mlisp.VString('Alice'), mlisp.VNumber(0), mlisp.VNumber(3)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Ali')
        v = mlisp.prim_string_substring('string-substring', [mlisp.VString('Alice'), mlisp.VNumber(2), mlisp.VNumber(3)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'i')
        v = mlisp.prim_string_substring('string-substring', [mlisp.VString('Alice'), mlisp.VNumber(0), mlisp.VNumber(0)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '')
        v = mlisp.prim_string_substring('string-substring', [mlisp.VString('Alice'), mlisp.VNumber(3), mlisp.VNumber(3)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '')


    def test_prim_apply(self):
        def prim(name, args):
            return (args[0], args[1])
        v = mlisp.prim_apply('apply', [mlisp.VPrimitive('test', prim, 2, 2),
                             _make_list([mlisp.VNumber(42), mlisp.VString('Alice')])])
        self.assertEqual(v[0].is_number(), True)
        self.assertEqual(v[0].value(), 42)
        self.assertEqual(v[1].is_string(), True)
        self.assertEqual(v[1].value(), 'Alice')
        v = mlisp.prim_apply('apply', [mlisp.VFunction(['a', 'b'], mlisp.Symbol('a'), mlisp.Environment()),
                             _make_list([mlisp.VNumber(42), mlisp.VString('Alice')])])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_prim_cons(self):
        v = mlisp.prim_cons('cons', [mlisp.VNumber(42), mlisp.VEmpty()])
        l = _unmake_list(v)
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 42)
        v = mlisp.prim_cons('cons', [mlisp.VNumber(42), _make_list([mlisp.VString('Alice'), mlisp.VString('Bob')])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 3)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 42)
        self.assertEqual(l[1].is_string(), True)
        self.assertEqual(l[1].value(), 'Alice')
        self.assertEqual(l[2].is_string(), True)
        self.assertEqual(l[2].value(), 'Bob')


    def test_prim_append(self):
        v = mlisp.prim_append('append', [])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = mlisp.prim_append('append', [_make_list([mlisp.VNumber(1), mlisp.VNumber(2)])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 2)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 1)
        self.assertEqual(l[1].is_number(), True)
        self.assertEqual(l[1].value(), 2)
        v = mlisp.prim_append('append', [_make_list([mlisp.VNumber(1), mlisp.VNumber(2)]),
                              _make_list([mlisp.VNumber(3), mlisp.VNumber(4)])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 4)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 1)
        self.assertEqual(l[1].is_number(), True)
        self.assertEqual(l[1].value(), 2)
        self.assertEqual(l[2].is_number(), True)
        self.assertEqual(l[2].value(), 3)
        self.assertEqual(l[3].is_number(), True)
        self.assertEqual(l[3].value(), 4)
        v = mlisp.prim_append('append', [_make_list([mlisp.VNumber(1), mlisp.VNumber(2)]),
                              _make_list([mlisp.VNumber(3), mlisp.VNumber(4)]),
                              _make_list([mlisp.VNumber(5), mlisp.VNumber(6)])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 6)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 1)
        self.assertEqual(l[1].is_number(), True)
        self.assertEqual(l[1].value(), 2)
        self.assertEqual(l[2].is_number(), True)
        self.assertEqual(l[2].value(), 3)
        self.assertEqual(l[3].is_number(), True)
        self.assertEqual(l[3].value(), 4)
        self.assertEqual(l[4].is_number(), True)
        self.assertEqual(l[4].value(), 5)
        self.assertEqual(l[5].is_number(), True)
        self.assertEqual(l[5].value(), 6)


    def test_prim_reverse(self):
        v = mlisp.prim_reverse('reverse', [_make_list([mlisp.VNumber(1),
                                           mlisp.VNumber(2),
                                           mlisp.VNumber(3),
                                           mlisp.VNumber(4)])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 4)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 4)
        self.assertEqual(l[1].is_number(), True)
        self.assertEqual(l[1].value(), 3)
        self.assertEqual(l[2].is_number(), True)
        self.assertEqual(l[2].value(), 2)
        self.assertEqual(l[3].is_number(), True)
        self.assertEqual(l[3].value(), 1)


    def test_prim_first(self):
        v = mlisp.prim_first('first', [_make_list([mlisp.VNumber(42)])])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        v = mlisp.prim_first('first', [_make_list([mlisp.VNumber(42),
                                         mlisp.VString('Alice'),
                                         mlisp.VString('Bob')])])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_prim_rest(self):
        v = mlisp.prim_rest('rest', [_make_list([mlisp.VNumber(42)])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = mlisp.prim_rest('rest', [_make_list([mlisp.VNumber(42),
                                        mlisp.VString('Alice'),
                                        mlisp.VString('Bob')])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 2)
        self.assertEqual(l[0].is_string(), True)
        self.assertEqual(l[0].value(), 'Alice')
        self.assertEqual(l[1].is_string(), True)
        self.assertEqual(l[1].value(), 'Bob')


    def test_prim_list(self):
        v = mlisp.prim_list('list', [])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = mlisp.prim_list('list', [mlisp.VNumber(42)])
        l = _unmake_list(v)
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 42)
        v = mlisp.prim_list('list', [mlisp.VNumber(42),
                                     mlisp.VString('Alice')])
        l = _unmake_list(v)
        self.assertEqual(len(l), 2)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 42)
        self.assertEqual(l[1].is_string(), True)
        self.assertEqual(l[1].value(), 'Alice')
        v = mlisp.prim_list('list', [mlisp.VNumber(42),
                                     mlisp.VString('Alice'),
                                     mlisp.VString('Bob')])
        l = _unmake_list(v)
        self.assertEqual(len(l), 3)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 42)
        self.assertEqual(l[1].is_string(), True)
        self.assertEqual(l[1].value(), 'Alice')
        self.assertEqual(l[2].is_string(), True)
        self.assertEqual(l[2].value(), 'Bob')


    def test_prim_length(self):
        v = mlisp.prim_length('length', [_make_list([])])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 0)
        v = mlisp.prim_length('length', [_make_list([mlisp.VNumber(42)])])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 1)
        v = mlisp.prim_length('length', [_make_list([mlisp.VNumber(42),
                                          mlisp.VString('Alice')])])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 2)
        v = mlisp.prim_length('length', [_make_list([mlisp.VNumber(42),
                                          mlisp.VString('Alice'),
                                          mlisp.VString('Bob')])])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 3)


    def test_prim_nth(self):
        v = mlisp.prim_nth('nth', [_make_list([mlisp.VNumber(42),
                                               mlisp.VString('Alice'),
                                               mlisp.VString('Bob')]),
                                   mlisp.VNumber(0)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        v = mlisp.prim_nth('nth', [_make_list([mlisp.VNumber(42),
                                               mlisp.VString('Alice'),
                                               mlisp.VString('Bob')]),
                                   mlisp.VNumber(1)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        v = mlisp.prim_nth('nth', [_make_list([mlisp.VNumber(42),
                                               mlisp.VString('Alice'),
                                               mlisp.VString('Bob')]),
                                   mlisp.VNumber(2)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Bob')


    def test_prim_map(self):
        def prim1(name, args):
            return args[0]
        def prim2(name, args):
            return args[1]
        v = mlisp.prim_map('map', [mlisp.VPrimitive('test', prim1, 1),
                                   _make_list([])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = mlisp.prim_map('map', [mlisp.VPrimitive('test', prim1, 1),
                                   _make_list([mlisp.VNumber(42),
                                               mlisp.VString('Alice'),
                                               mlisp.VString('Bob')])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 3)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 42)
        self.assertEqual(l[1].is_string(), True)
        self.assertEqual(l[1].value(), 'Alice')
        self.assertEqual(l[2].is_string(), True)
        self.assertEqual(l[2].value(), 'Bob')
        v = mlisp.prim_map('map', [mlisp.VPrimitive('test', prim2, 2),
                                   _make_list([]),
                                   _make_list([])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = mlisp.prim_map('map', [mlisp.VPrimitive('test', prim2, 2),
                                   _make_list([]),
                                   _make_list([mlisp.VNumber(42)])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = mlisp.prim_map('map', [mlisp.VPrimitive('test', prim2, 2),
                                   _make_list([mlisp.VNumber(42),
                                               mlisp.VString('Alice'),
                                               mlisp.VString('Bob')]),
                                   _make_list([mlisp.VNumber(84),
                                               mlisp.VString('Charlie'),
                                               mlisp.VString('Darlene')])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 3)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 84)
        self.assertEqual(l[1].is_string(), True)
        self.assertEqual(l[1].value(), 'Charlie')
        self.assertEqual(l[2].is_string(), True)
        self.assertEqual(l[2].value(), 'Darlene')


    def test_prim_filter(self):
        def prim_none(name, args):
            return mlisp.VBoolean(False)
        def prim_int(name, args):
            return mlisp.VBoolean(args[0].is_number())
        v = mlisp.prim_filter('filter', [mlisp.VPrimitive('test', prim_none, 1),
                                         _make_list([])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = mlisp.prim_filter('filter', [mlisp.VPrimitive('test', prim_none, 1),
                                         _make_list([mlisp.VNumber(42),
                                                     mlisp.VString('Alice'),
                                                     mlisp.VString('Bob')])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = mlisp.prim_filter('filter', [mlisp.VPrimitive('test', prim_int, 1),
                                         _make_list([mlisp.VNumber(42),
                                                     mlisp.VString('Alice'),
                                                     mlisp.VString('Bob')])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 42)


    def test_prim_foldr(self):
        def prim(name, args):
            return mlisp.VString(args[0].value() + '(' + args[1].value() + ')')
        v = mlisp.prim_foldr('foldr', [mlisp.VPrimitive('test', prim, 2),
                                       _make_list([]),
                                       mlisp.VString('base')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'base')
        v = mlisp.prim_foldr('foldr', [mlisp.VPrimitive('test', prim, 2),
                                       _make_list([mlisp.VString('Alice'),
                                                   mlisp.VString('Bob'),
                                                   mlisp.VString('Charlie')]),
                                       mlisp.VString('base')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice(Bob(Charlie(base)))')


    def test_prim_foldl(self):
        def prim(name, args):
            return mlisp.VString('(' + args[0].value() + ')' + args[1].value())
        v = mlisp.prim_foldl('foldl', [mlisp.VPrimitive('test', prim, 2),
                                       mlisp.VString('base'),
                                       _make_list([])])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'base')
        v = mlisp.prim_foldl('foldl', [mlisp.VPrimitive('test', prim, 2),
                                       mlisp.VString('base'),
                                       _make_list([mlisp.VString('Alice'),
                                                   mlisp.VString('Bob'),
                                                   mlisp.VString('Charlie')])])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '(((base)Alice)Bob)Charlie')


    def test_prim_eqp(self):
        v = mlisp.prim_eqp('eq?', [mlisp.VNumber(42),
                                   mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_eqp('eq?', [mlisp.VNumber(42),
                                   mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        lst = _make_list([mlisp.VNumber(42)])
        v = mlisp.prim_eqp('eq?', [lst, lst])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_eqp('eq?', [lst, _make_list([mlisp.VNumber(42)])])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_eqp('eq?', [lst, mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_eqp('eq?', [lst, _make_list([mlisp.VNumber(84)])])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_eqlp(self):
        v = mlisp.prim_eqlp('eql?', [mlisp.VNumber(42),
                           mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_eqlp('eql?', [mlisp.VNumber(42),
                           mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        lst = _make_list([mlisp.VNumber(42)])
        v = mlisp.prim_eqlp('eql?', [lst, lst])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_eqlp('eql?', [lst, _make_list([mlisp.VNumber(42)])])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_eqlp('eql?', [lst, mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_eqlp('eql?', [lst, _make_list([mlisp.VNumber(84)])])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_emptyp(self):
        v = mlisp.prim_emptyp('empty?', [mlisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_emptyp('empty?', [mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_emptyp('empty?', [mlisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_emptyp('empty?', [mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_emptyp('empty?', [mlisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_emptyp('empty?', [mlisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_emptyp('empty?', [mlisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_emptyp('empty?', [mlisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_emptyp('empty?', [mlisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = mlisp.prim_emptyp('empty?', [mlisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_emptyp('empty?', [mlisp.VFunction(['a'], mlisp.VSymbol('a'), mlisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_consp(self):
        v = mlisp.prim_consp('cons?', [mlisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_consp('cons?', [mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_consp('cons?', [mlisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_consp('cons?', [mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_consp('cons?', [mlisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_consp('cons?', [mlisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_consp('cons?', [mlisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_consp('cons?', [mlisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_consp('cons?', [mlisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = mlisp.prim_consp('cons?', [mlisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_consp('cons?', [mlisp.VFunction(['a'], mlisp.VSymbol('a'), mlisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_listp(self):
        v = mlisp.prim_listp('list?', [mlisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_listp('list?', [mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_listp('list?', [mlisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_listp('list?', [mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_listp('list?', [mlisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_listp('list?', [mlisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_listp('list?', [mlisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_listp('list?', [mlisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_listp('list?', [mlisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = mlisp.prim_listp('list?', [mlisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_listp('list?', [mlisp.VFunction(['a'], mlisp.VSymbol('a'), mlisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_numberp(self):
        v = mlisp.prim_numberp('number?', [mlisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numberp('number?', [mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numberp('number?', [mlisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numberp('number?', [mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_numberp('number?', [mlisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numberp('number?', [mlisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numberp('number?', [mlisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numberp('number?', [mlisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numberp('number?', [mlisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = mlisp.prim_numberp('number?', [mlisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numberp('number?', [mlisp.VFunction(['a'], mlisp.VSymbol('a'), mlisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_booleanp(self):
        v = mlisp.prim_booleanp('boolean?', [mlisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_booleanp('boolean?', [mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_booleanp('boolean?', [mlisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_booleanp('boolean?', [mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_booleanp('boolean?', [mlisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_booleanp('boolean?', [mlisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_booleanp('boolean?', [mlisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_booleanp('boolean?', [mlisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_booleanp('boolean?', [mlisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = mlisp.prim_booleanp('boolean?', [mlisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_booleanp('boolean?', [mlisp.VFunction(['a'], mlisp.VSymbol('a'), mlisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_stringp(self):
        v = mlisp.prim_stringp('string?', [mlisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_stringp('string?', [mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_stringp('string?', [mlisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_stringp('string?', [mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_stringp('string?', [mlisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_stringp('string?', [mlisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_stringp('string?', [mlisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_stringp('string?', [mlisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_stringp('string?', [mlisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = mlisp.prim_stringp('string?', [mlisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_stringp('string?', [mlisp.VFunction(['a'], mlisp.VSymbol('a'), mlisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_symbolp(self):
        v = mlisp.prim_symbolp('symbol?', [mlisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_symbolp('symbol?', [mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_symbolp('symbol?', [mlisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_symbolp('symbol?', [mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_symbolp('symbol?', [mlisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_symbolp('symbol?', [mlisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_symbolp('symbol?', [mlisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_symbolp('symbol?', [mlisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_symbolp('symbol?', [mlisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = mlisp.prim_symbolp('symbol?', [mlisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_symbolp('symbol?', [mlisp.VFunction(['a'], mlisp.VSymbol('a'), mlisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_functionp(self):
        v = mlisp.prim_functionp('function?', [mlisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_functionp('function?', [mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_functionp('function?', [mlisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_functionp('function?', [mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_functionp('function?', [mlisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_functionp('function?', [mlisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_functionp('function?', [mlisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_functionp('function?', [mlisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_functionp('function?', [mlisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = mlisp.prim_functionp('function?', [mlisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_functionp('function?', [mlisp.VFunction(['a'], mlisp.VSymbol('a'), mlisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)


    def test_prim_nilp(self):
        v = mlisp.prim_nilp('nil?', [mlisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_nilp('nil?', [mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_nilp('nil?', [mlisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_nilp('nil?', [mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_nilp('nil?', [mlisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_nilp('nil?', [mlisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_nilp('nil?', [mlisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_nilp('nil?', [mlisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_nilp('nil?', [mlisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True )
        v = mlisp.prim_nilp('nil?', [mlisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_nilp('nil?', [mlisp.VFunction(['a'], mlisp.VSymbol('a'), mlisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)



    
#
# Engine
#

class TestEngine(TestCase):
    
    def test_engine_read(self):
        engine = mlisp.Engine()
        # integer
        inp = '42'
        s = engine.read(inp)
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.is_number(), True)
        self.assertEqual(s.value(), 42)
        # cons
        inp = '(42 Alice Bob)'
        s = engine.read(inp)
        self.assertEqual(s.is_atom(), False)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), True)
        self.assertEqual(s.is_cons(), True)
        self.assertEqual(s.car().is_number(), True)
        self.assertEqual(s.car().value(), 42)
        self.assertEqual(s.cdr().is_cons(), True)
        self.assertEqual(s.cdr().car().is_symbol(), True)
        self.assertEqual(s.cdr().car().value(), 'alice')
        self.assertEqual(s.cdr().cdr().is_cons(), True)
        self.assertEqual(s.cdr().cdr().car().is_symbol(), True)
        self.assertEqual(s.cdr().cdr().car().value(), 'bob')
        self.assertEqual(s.cdr().cdr().cdr().is_empty(), True)


    def test_engine_eval(self):
        # integer
        engine = mlisp.Engine()
        inp = _make_list(mlisp.VNumber(42))
        v = engine.eval(inp)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # application
        engine = mlisp.Engine()
        inp = _make_list([[mlisp.VSymbol('fn'), [mlisp.VSymbol('a'), mlisp.VSymbol('b')], mlisp.VSymbol('a')], mlisp.VNumber(42), mlisp.VNumber(0)])
        v = engine.eval(inp)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # define
        engine = mlisp.Engine()
        inp = _make_list([mlisp.VSymbol('def'), mlisp.VSymbol('a'), mlisp.VNumber(42)])
        engine.eval(inp)
        v = engine.eval(_make_list(mlisp.VSymbol('a')))
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # defun
        engine = mlisp.Engine()
        inp = _make_list([mlisp.VSymbol('def'), [mlisp.VSymbol('foo'), mlisp.VSymbol('a')], mlisp.VSymbol('a')])
        engine.eval(inp)
        v = engine.eval(_make_list([mlisp.VSymbol('foo'), mlisp.VNumber(42)]))
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)

        
    def test_engine_new_env(self):
        # one env
        engine = mlisp.Engine()
        engine.new_env(bindings=[('a', mlisp.VNumber(42)), ('b', mlisp.VString('Alice'))])
        v = engine.eval(engine.read('a'))
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        v = engine.eval(engine.read('empty'))
        self.assertEqual(v.is_empty(), True)
        # two envs
        engine = mlisp.Engine()
        engine.new_env(bindings=[('x', mlisp.VNumber(42)), ('y', mlisp.VString('Alice'))])
        engine.new_env(bindings=[('a', mlisp.VNumber(42)), ('b', mlisp.VString('Alice'))])
        v = engine.eval(engine.read('a'))
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        v = engine.eval(engine.read('b'))
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        v = engine.eval(engine.read('empty'))
        self.assertEqual(v.is_empty(), True)
        v = engine.eval(engine.read('y'))
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')


    def test_engine_balance(self):
        engine = mlisp.Engine()
        self.assertEqual(engine.balance('hello'), True)
        self.assertEqual(engine.balance('hello ()'), True)
        self.assertEqual(engine.balance('()'), True)
        self.assertEqual(engine.balance('(1 2 (3 4) 5)'), True)
        self.assertEqual(engine.balance('(()()())'), True)
        self.assertEqual(engine.balance('())'), True)
        self.assertEqual(engine.balance('(1 2 3 (4 5) 6))()'), True)
        self.assertEqual(engine.balance('(\u00e9 \u00ea 3 (4 5) 6))()'), True)
        self.assertEqual(engine.balance('('), False)
        self.assertEqual(engine.balance('hello ('), False)
        self.assertEqual(engine.balance('(()'), False)
        self.assertEqual(engine.balance('( 1 2 (4)'), False)
        self.assertEqual(engine.balance('( 1 2 (()(()(('), False)
    
    
