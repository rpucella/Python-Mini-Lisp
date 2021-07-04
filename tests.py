from unittest import TestCase

import mlisp

# TODO - share testing function between the various pieces that have commonality
#  e.g., parse_sexp_int <- used to test both parse_sexp() and to test engine.read()


def _make_sexp(struct):
    if type(struct) == type([]):
        result = mlisp.SEmpty()
        for r in reversed(struct):
            result = mlisp.SCons(_make_sexp(r), result)
        return result
    else:
        return mlisp.SAtom(struct)

    
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
        self.assertEqual(b.type(), 'boolean')
        self.assertEqual(b.is_number(), False)
        self.assertEqual(b.is_boolean(), True)
        self.assertEqual(b.is_string(), False)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_reference(), False)
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
        self.assertEqual(b.type(), 'boolean')
        self.assertEqual(b.is_number(), False)
        self.assertEqual(b.is_boolean(), True)
        self.assertEqual(b.is_string(), False)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_reference(), False)
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
        self.assertEqual(b.type(), 'string')
        self.assertEqual(b.is_number(), False)
        self.assertEqual(b.is_boolean(), False)
        self.assertEqual(b.is_string(), True)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_reference(), False)
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
        self.assertEqual(b.type(), 'string')
        self.assertEqual(b.is_number(), False)
        self.assertEqual(b.is_boolean(), False)
        self.assertEqual(b.is_string(), True)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_reference(), False)
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
        self.assertEqual(b.type(), 'number')
        self.assertEqual(b.is_number(), True)
        self.assertEqual(b.is_boolean(), False)
        self.assertEqual(b.is_string(), False)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_reference(), False)
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
        self.assertEqual(b.type(), 'number')
        self.assertEqual(b.is_number(), True)
        self.assertEqual(b.is_boolean(), False)
        self.assertEqual(b.is_string(), False)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_reference(), False)
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
        self.assertEqual(b.type(), 'nil')
        self.assertEqual(b.is_number(), False)
        self.assertEqual(b.is_boolean(), False)
        self.assertEqual(b.is_string(), False)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), True)
        self.assertEqual(b.is_reference(), False)
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


class TestValueReference(TestCase):

    def test_num(self):
        # num
        val = mlisp.VNumber(42)
        r = mlisp.VReference(val)
        self.assertEqual(str(r), '#(ref 42)')
        self.assertEqual(r.display(), '#(ref 42)')
        self.assertEqual(r.type(), 'ref')
        self.assertEqual(r.is_number(), False)
        self.assertEqual(r.is_boolean(), False)
        self.assertEqual(r.is_string(), False)
        self.assertEqual(r.is_symbol(), False)
        self.assertEqual(r.is_nil(), False)
        self.assertEqual(r.is_reference(), True)
        self.assertEqual(r.is_empty(), False)
        self.assertEqual(r.is_cons(), False)
        self.assertEqual(r.is_function(), False)
        self.assertEqual(r.is_atom(), False)
        self.assertEqual(r.is_list(), False)
        self.assertEqual(r.is_true(), True)
        self.assertEqual(r.is_equal(mlisp.VReference(val)), True)
        self.assertEqual(r.is_equal(mlisp.VReference(mlisp.VNumber(42))), True)
        self.assertEqual(r.is_equal(mlisp.VReference(mlisp.VNumber(0))), False)
        self.assertEqual(r.is_equal(mlisp.VReference(mlisp.VString("Alice"))), False)
        self.assertEqual(r.is_eq(mlisp.VReference(val)), False)
        self.assertEqual(r.is_eq(mlisp.VReference(mlisp.VNumber(42))), False)
        self.assertEqual(r.is_eq(mlisp.VReference(mlisp.VNumber(0))), False)
        self.assertEqual(r.is_eq(mlisp.VReference(mlisp.VString("Alice"))), False)
        self.assertEqual(r.is_equal(r), True)
        self.assertEqual(r.is_eq(r), True)
        self.assertEqual(r.value(), val)

    def test_string(self):
        # string
        val = mlisp.VString("Alice")
        r = mlisp.VReference(val)
        self.assertEqual(str(r), '#(ref "Alice")')
        self.assertEqual(r.display(), '#(ref "Alice")')
        self.assertEqual(r.type(), 'ref')
        self.assertEqual(r.is_number(), False)
        self.assertEqual(r.is_boolean(), False)
        self.assertEqual(r.is_string(), False)
        self.assertEqual(r.is_symbol(), False)
        self.assertEqual(r.is_nil(), False)
        self.assertEqual(r.is_reference(), True)
        self.assertEqual(r.is_empty(), False)
        self.assertEqual(r.is_cons(), False)
        self.assertEqual(r.is_function(), False)
        self.assertEqual(r.is_atom(), False)
        self.assertEqual(r.is_list(), False)
        self.assertEqual(r.is_true(), True)
        self.assertEqual(r.is_equal(mlisp.VReference(mlisp.VNumber(42))), False)
        self.assertEqual(r.is_equal(mlisp.VReference(val)), True)
        self.assertEqual(r.is_equal(mlisp.VReference(mlisp.VString("Alice"))), True)
        self.assertEqual(r.is_equal(mlisp.VReference(mlisp.VString("Bob"))), False)
        self.assertEqual(r.is_eq(mlisp.VReference(mlisp.VNumber(42))), False)
        self.assertEqual(r.is_eq(mlisp.VReference(val)), False)
        self.assertEqual(r.is_eq(mlisp.VReference(mlisp.VString("Alice"))), False)
        self.assertEqual(r.is_eq(mlisp.VReference(mlisp.VString("Bob"))), False)
        self.assertEqual(r.is_equal(r), True)
        self.assertEqual(r.is_eq(r), True)
        self.assertEqual(r.value(), val)

    def test_nested(self):
        # nested
        val = mlisp.VReference(mlisp.VNumber(42))
        r = mlisp.VReference(val)
        self.assertEqual(str(r), '#(ref #(ref 42))')
        self.assertEqual(r.display(), '#(ref #(ref 42))')
        self.assertEqual(r.type(), 'ref')
        self.assertEqual(r.is_number(), False)
        self.assertEqual(r.is_boolean(), False)
        self.assertEqual(r.is_string(), False)
        self.assertEqual(r.is_symbol(), False)
        self.assertEqual(r.is_nil(), False)
        self.assertEqual(r.is_reference(), True)
        self.assertEqual(r.is_empty(), False)
        self.assertEqual(r.is_cons(), False)
        self.assertEqual(r.is_function(), False)
        self.assertEqual(r.is_atom(), False)
        self.assertEqual(r.is_list(), False)
        self.assertEqual(r.is_true(), True)
        self.assertEqual(r.is_equal(mlisp.VReference(val)), True)
        self.assertEqual(r.is_equal(mlisp.VReference(mlisp.VReference(mlisp.VNumber(42)))), True)
        self.assertEqual(r.is_equal(mlisp.VReference(mlisp.VNumber(42))), False)
        self.assertEqual(r.is_eq(mlisp.VReference(val)), False)
        self.assertEqual(r.is_eq(mlisp.VReference(mlisp.VReference(mlisp.VNumber(42)))), False)
        self.assertEqual(r.is_eq(mlisp.VReference(mlisp.VNumber(42))), False)
        self.assertEqual(r.is_equal(r), True)
        self.assertEqual(r.is_eq(r), True)
        self.assertEqual(r.value(), val)
    

class TestValueEmpty(TestCase):
    
    def test_empty(self):
        b = mlisp.VEmpty()
        self.assertEqual(str(b), '()')
        self.assertEqual(b.display(), '()')
        self.assertEqual(b.type(), 'empty-list')
        self.assertEqual(b.is_number(), False)
        self.assertEqual(b.is_boolean(), False)
        self.assertEqual(b.is_string(), False)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_reference(), False)
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
        self.assertEqual(b.type(), 'cons-list')
        self.assertEqual(b.is_number(), False)
        self.assertEqual(b.is_boolean(), False)
        self.assertEqual(b.is_string(), False)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_reference(), False)
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
        self.assertEqual(b.type(), 'cons-list')
        self.assertEqual(b.is_number(), False)
        self.assertEqual(b.is_boolean(), False)
        self.assertEqual(b.is_string(), False)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_reference(), False)
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
        def prim (args):
            return (args[0], args[1])
        i = mlisp.VNumber(42)
        j = mlisp.VNumber(0)
        b = mlisp.VPrimitive('test', prim, 2)
        self.assertEqual(str(b).startswith('#[prim '), True)
        self.assertEqual(b.display().startswith('#[prim '), True)
        self.assertEqual(b.type(), 'primitive')
        self.assertEqual(b.is_number(), False)
        self.assertEqual(b.is_boolean(), False)
        self.assertEqual(b.is_string(), False)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_reference(), False)
        self.assertEqual(b.is_empty(), False)
        self.assertEqual(b.is_cons(), False)
        self.assertEqual(b.is_function(), True)
        self.assertEqual(b.is_atom(), True)
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
        self.assertEqual(b.type(), 'symbol')
        self.assertEqual(b.is_number(), False)
        self.assertEqual(b.is_boolean(), False)
        self.assertEqual(b.is_string(), False)
        self.assertEqual(b.is_symbol(), True)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_reference(), False)
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
        self.assertEqual(b.type(), 'function')
        self.assertEqual(b.is_number(), False)
        self.assertEqual(b.is_boolean(), False)
        self.assertEqual(b.is_string(), False)
        self.assertEqual(b.is_symbol(), False)
        self.assertEqual(b.is_nil(), False)
        self.assertEqual(b.is_reference(), False)
        self.assertEqual(b.is_empty(), False)
        self.assertEqual(b.is_cons(), False)
        self.assertEqual(b.is_function(), True)
        self.assertEqual(b.is_atom(), True)
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
# SExpressions
#

class TestSExp(TestCase):
    
    def test_symbol(self):
        s = mlisp.SAtom('Alice')
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.content(), 'Alice')
        self.assertEqual(s.as_value().is_symbol(), True)
        self.assertEqual(s.as_value().value(), 'alice')
        # accents
        s = mlisp.SAtom('TEST\u00c9')
        self.assertEqual(s.content(), 'TEST\u00c9')
        self.assertEqual(s.as_value().value(), 'test\u00e9')


    def test_string(self):
        s = mlisp.SAtom('"Alice"')
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.content(), '"Alice"')
        self.assertEqual(s.as_value().is_string(), True)
        self.assertEqual(s.as_value().value(), 'Alice')
        # accents
        s = mlisp.SAtom('"Test\u00e9"')
        self.assertEqual(s.content(), '"Test\u00e9"')
        self.assertEqual(s.as_value().value(), 'Test\u00e9')


    def test_integer(self):
        s = mlisp.SAtom('42')
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.content(), '42')
        self.assertEqual(s.as_value().is_number(), True)
        self.assertEqual(s.as_value().value(), 42)


    def test_boolean(self):
        s = mlisp.SAtom('#t')
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.content(), '#t')
        self.assertEqual(s.as_value().is_boolean(), True)
        self.assertEqual(s.as_value().value(), True)
        s = mlisp.SAtom('#f')
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.content(), '#f')
        self.assertEqual(s.as_value().is_boolean(), True)
        self.assertEqual(s.as_value().value(), False)


    def test_empty(self):
        s = mlisp.SEmpty()
        self.assertEqual(s.is_atom(), False)
        self.assertEqual(s.is_empty(), True)
        self.assertEqual(s.is_cons(), False)
        self.assertIs(s.content(), None)
        self.assertEqual(s.as_value().is_empty(), True)


    def test_cons(self):
        car = mlisp.SAtom('42')
        cdr = mlisp.SEmpty()
        s = mlisp.SCons(car, cdr)
        self.assertEqual(s.is_atom(), False)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), True)
        self.assertEqual(s.content(), (car, cdr))
        self.assertEqual(s.as_value().is_cons(), True)
        self.assertEqual(s.as_value().car().is_number(), True)
        self.assertEqual(s.as_value().car().value(), 42)
        self.assertEqual(s.as_value().cdr().is_empty(), True)
    
    def test_from_value(self):
        v = mlisp.VBoolean(True)
        self.assertEqual(mlisp.SExpression.from_value(v).is_atom(), True)
        self.assertEqual(mlisp.SExpression.from_value(v).content(), '#true')
        v = mlisp.VBoolean(False)
        self.assertEqual(mlisp.SExpression.from_value(v).is_atom(), True)
        self.assertEqual(mlisp.SExpression.from_value(v).content(), '#false')
        v = mlisp.VString('Alice')
        self.assertEqual(mlisp.SExpression.from_value(v).is_atom(), True)
        self.assertEqual(mlisp.SExpression.from_value(v).content(), '"Alice"')
        v = mlisp.VString('Test\u00e9')
        self.assertEqual(mlisp.SExpression.from_value(v).is_atom(), True)
        self.assertEqual(mlisp.SExpression.from_value(v).content(), '"Test\u00e9"')
        v = mlisp.VNumber(42)
        self.assertEqual(mlisp.SExpression.from_value(v).is_atom(), True)
        self.assertEqual(mlisp.SExpression.from_value(v).content(), '42')
        #v = mlisp.VNil()
        #self.assertEqual(mlisp.SExpression.from_value(v).is_atom(), True)
        #self.assertEqual(mlisp.SExpression.from_value(v).content(), 'NIL')
        v = mlisp.VSymbol('Alice')
        self.assertEqual(mlisp.SExpression.from_value(v).is_atom(), True)
        self.assertEqual(mlisp.SExpression.from_value(v).content(), 'alice')
        v = mlisp.VSymbol('TEST\u00c9')
        self.assertEqual(mlisp.SExpression.from_value(v).is_atom(), True)
        self.assertEqual(mlisp.SExpression.from_value(v).content(), 'test\u00e9')
        v = mlisp.VEmpty()
        self.assertEqual(mlisp.SExpression.from_value(v).is_empty(), True)
        v = mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())
        self.assertEqual(mlisp.SExpression.from_value(v).is_cons(), True)
        self.assertEqual(mlisp.SExpression.from_value(v).content()[0].is_atom(), True)
        self.assertEqual(mlisp.SExpression.from_value(v).content()[0].content(), '42')
        self.assertEqual(mlisp.SExpression.from_value(v).content()[1].is_empty(), True)
    
        # function? primitive? -- these might be unreadable!?
    


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
        s = mlisp.SAtom('Alice')
        e = mlisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'alice')
        # symobl (accents)
        s = mlisp.SAtom('TEST\u00c9')
        e = mlisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'test\u00e9')
        # string
        s = mlisp.SAtom('"Alice"')
        e = mlisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        # string (accents)
        s = mlisp.SAtom('"Test\u00e9"')
        e = mlisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Test\u00e9')
        # integer
        s = mlisp.SAtom('42')
        e = mlisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # boolean
        s = mlisp.SAtom('#t')
        e = mlisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        s = mlisp.SAtom('#f')
        e = mlisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        # empty
        s = mlisp.SEmpty()
        e = mlisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_empty(), True)
        # cons
        s = mlisp.SCons(mlisp.SAtom('42'), mlisp.SEmpty())
        e = mlisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_cons(), True)
        self.assertEqual(v.car().is_number(), True)
        self.assertEqual(v.car().value(), 42)
        self.assertEqual(v.cdr().is_empty(), True)
        # cons 2
        s = mlisp.SCons(mlisp.SAtom('42'), mlisp.SCons(mlisp.SAtom('Alice'), mlisp.SEmpty()))
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

    def test_sexp_to_exp(self):
        env = mlisp.Environment(bindings=[('a', mlisp.VNumber(42))])
        # symbol
        s = mlisp.SAtom('a')
        v = s.to_expression().eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # string
        s = mlisp.SAtom('"Alice"')
        v = s.to_expression().eval(env)
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        # integer
        s = mlisp.SAtom('42')
        v = s.to_expression().eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # boolean
        s = mlisp.SAtom('#t')
        v = s.to_expression().eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        s = mlisp.SAtom('#f')
        v = s.to_expression().eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
    

#
# SExpression parsing
#

class TestSExpParsing(TestCase):
    
    def test_sexp_parse_symbol(self):
        inp = 'Alice'
        (s, rest) = mlisp.parse_sexp(inp)
        self.assertEqual(rest, '')
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.content(), 'Alice')
        self.assertEqual(s.as_value().is_symbol(), True)
        self.assertEqual(s.as_value().value(), 'alice')
        # accents
        inp = 'TEST\u00c9'
        (s, rest) = mlisp.parse_sexp(inp)
        self.assertEqual(s.content(), 'TEST\u00c9')
        self.assertEqual(s.as_value().is_symbol(), True)
        self.assertEqual(s.as_value().value(), 'test\u00e9')


    def test_sexp_parse_string(self):
        inp = '"Alice"'
        (s, rest) = mlisp.parse_sexp(inp)
        self.assertEqual(rest, '')
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.content(), '"Alice"')
        self.assertEqual(s.as_value().is_string(), True)
        self.assertEqual(s.as_value().value(), 'Alice')
        # accents
        inp = '"Test\u00e9"'
        (s, rest) = mlisp.parse_sexp(inp)
        self.assertEqual(s.content(), '"Test\u00e9"')
        self.assertEqual(s.as_value().is_string(), True)
        self.assertEqual(s.as_value().value(), 'Test\u00e9')


    def test_sexp_parse_integer(self):
        inp = '42'
        (s, rest) = mlisp.parse_sexp(inp)
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.content(), '42')
        self.assertEqual(s.as_value().is_number(), True)
        self.assertEqual(s.as_value().value(), 42)


    def test_sexp_parse_boolean(self):
        inp = '#t'
        (s, rest) = mlisp.parse_sexp(inp)
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.content(), '#t')
        self.assertEqual(s.as_value().is_boolean(), True)
        self.assertEqual(s.as_value().value(), True)
        inp = '#f'
        (s, rest) = mlisp.parse_sexp(inp)
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.content(), '#f')
        self.assertEqual(s.as_value().is_boolean(), True)
        self.assertEqual(s.as_value().value(), False)


    def test_sexp_parse_empty(self):
        inp = '()'
        (s, rest) = mlisp.parse_sexp(inp)
        self.assertEqual(s.is_atom(), False)
        self.assertEqual(s.is_empty(), True)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.content(), None)
        self.assertEqual(s.as_value().is_empty(), True)


    def test_sexp_parse_cons(self):
        inp = '(42 Alice Bob)'
        (s, rest) = mlisp.parse_sexp(inp)
        self.assertEqual(s.is_atom(), False)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), True)
        self.assertEqual(s.as_value().is_cons(), True)
        self.assertEqual(s.as_value().car().is_number(), True)
        self.assertEqual(s.as_value().car().value(), 42)
        self.assertEqual(s.as_value().cdr().is_cons(), True)
        self.assertEqual(s.as_value().cdr().car().is_symbol(), True)
        self.assertEqual(s.as_value().cdr().car().value(), 'alice')
        self.assertEqual(s.as_value().cdr().cdr().is_cons(), True)
        self.assertEqual(s.as_value().cdr().cdr().car().is_symbol(), True)
        self.assertEqual(s.as_value().cdr().cdr().car().value(), 'bob')
        self.assertEqual(s.as_value().cdr().cdr().cdr().is_empty(), True)


    def test_sexp_parse_cons_nested(self):
        inp = '((42 Alice) ((Bob)))'
        (s, rest) = mlisp.parse_sexp(inp)
        self.assertEqual(s.is_atom(), False)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), True)
        self.assertEqual(s.as_value().is_cons(), True)
        # (42 Alice)
        self.assertEqual(s.as_value().car().is_cons(), True)
        self.assertEqual(s.as_value().car().car().is_number(), True)
        self.assertEqual(s.as_value().car().car().value(), 42)
        self.assertEqual(s.as_value().car().cdr().is_cons(), True)
        self.assertEqual(s.as_value().car().cdr().car().is_symbol(), True)
        self.assertEqual(s.as_value().car().cdr().car().value(), 'alice')
        self.assertEqual(s.as_value().car().cdr().cdr().is_empty(), True)
        self.assertEqual(s.as_value().cdr().is_cons(), True)
        # ((Bob))
        self.assertEqual(s.as_value().cdr().car().is_cons(), True)
        self.assertEqual(s.as_value().cdr().car().car().is_cons(), True)
        self.assertEqual(s.as_value().cdr().car().car().car().is_symbol(), True)
        self.assertEqual(s.as_value().cdr().car().car().car().value(), 'bob')
        self.assertEqual(s.as_value().cdr().car().car().cdr().is_empty(), True)
        self.assertEqual(s.as_value().cdr().car().cdr().is_empty(), True)
        self.assertEqual(s.as_value().cdr().cdr().is_empty(), True)


    def test_sexp_parse_rest(self):
        inp = '42 xyz'
        (s, rest) = mlisp.parse_sexp(inp)
        self.assertEqual(rest, ' xyz')
        inp = 'Alice xyz'
        (s, rest) = mlisp.parse_sexp(inp)
        self.assertEqual(rest, ' xyz')
        inp = '"Alice" xyz'
        (s, rest) = mlisp.parse_sexp(inp)
        self.assertEqual(rest, ' xyz')
        inp = '#t xyz'
        (s, rest) = mlisp.parse_sexp(inp)
        self.assertEqual(rest, ' xyz')
        inp = '#f xyz'
        (s, rest) = mlisp.parse_sexp(inp)
        self.assertEqual(rest, ' xyz')
        inp = '() xyz'
        (s, rest) = mlisp.parse_sexp(inp)
        self.assertEqual(rest, ' xyz')
        inp = '(Alice Bob) xyz'
        (s, rest) = mlisp.parse_sexp(inp)
        self.assertEqual(rest, ' xyz')
    

    
#
# Expression parsing
#


class TestExpParsing(TestCase):

    
    def test_exp_parse_symbol(self):
        env = mlisp.Environment(bindings=[('Alice', mlisp.VNumber(42))])
        inp = _make_sexp('Alice')
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # accents
        env = mlisp.Environment(bindings=[('Test\u00e9', mlisp.VNumber(42))])
        inp = _make_sexp('Test\u00e9')
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_exp_parse_string(self):
        env = mlisp.Environment()
        inp = _make_sexp('"Alice"')
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        # accents
        inp = _make_sexp('"Test\u00e9"')
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Test\u00e9')


    def test_exp_parse_integer(self):
        env = mlisp.Environment()
        inp = _make_sexp('42')
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_exp_parse_boolean(self):
        env = mlisp.Environment()
        inp = _make_sexp('#t')
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        inp = _make_sexp('#f')
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_exp_parse_if(self):
        # then branch
        env = mlisp.Environment([('a', mlisp.VNumber(42))])
        inp = _make_sexp(['if', '#t', 'a', '#f'])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # else branch
        inp = _make_sexp(['if', '#f', '#f', 'a'])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_exp_parse_lambda(self):
        # simple
        env = mlisp.Environment()
        inp = _make_sexp(['fn', ['a', 'b'], 'a'])
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
        inp = _make_sexp(['f', 'a', 'b'])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_exp_parse_quote(self):
        env = mlisp.Environment()
        # symbol
        inp = _make_sexp(['quote', 'Alice'])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'alice')
        # empty
        inp = _make_sexp(['quote', []])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_empty(), True)
        # cons
        inp = _make_sexp(['quote', ['42']])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_cons(), True)
        self.assertEqual(v.car().is_number(), True)
        self.assertEqual(v.car().value(), 42)
        self.assertEqual(v.cdr().is_empty(), True)


    def test_exp_parse_do(self):
        env = mlisp.Environment(bindings=[('a', mlisp.VNumber(42))])
        # empty
        inp = _make_sexp(['do'])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_nil(), True)
        # single
        inp = _make_sexp(['do', 'a'])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # many
        inp = _make_sexp(['do', '0', '1', 'a'])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_exp_parse_letrec(self):
        env = mlisp.Environment(bindings=[('a', mlisp.VNumber(42))])
        # empty
        inp = _make_sexp(['letrec', [], 'a'])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # many
        inp = _make_sexp(['letrec', [['one', ['fn', ['x', 'y'], 'two']],
                                     ['two', ['fn', ['x'], 'a']]],
                          ['one', '0', '0']])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_function(), True)
        v = v.apply([mlisp.VNumber(0)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_exp_parse_let(self):
        env = mlisp.Environment(bindings=[('a', mlisp.VNumber(42))])
        # empty
        inp = _make_sexp(['let', [], 'a'])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # many
        inp = _make_sexp(['let', [['a', '84'], ['b', 'a']], 'a'])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 84)
        inp = _make_sexp(['let', [['a', '84'], ['b', 'a']], 'b'])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_exp_parse_letstar(self):
        env = mlisp.Environment(bindings=[('a', mlisp.VNumber(42))])
        # empty
        inp = _make_sexp(['let*', [], 'a'])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # many
        inp = _make_sexp(['let*', [['a', '84'], ['b', 'a']], 'a'])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 84)
        inp = _make_sexp(['let*', [['a', '84'], ['b', 'a']], 'b'])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 84)


    def test_exp_parse_and(self):
        env = mlisp.Environment(bindings=[('a', mlisp.VNumber(42))])
        # empty
        inp = _make_sexp(['and'])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        # many
        inp = _make_sexp(['and', 'a'])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        inp = _make_sexp(['and', '1', 'a' ])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        inp = _make_sexp(['and', '1', '2', 'a' ])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        inp = _make_sexp(['and', '0', '2', 'a' ])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 0)
        inp = _make_sexp(['and', '1', '#f', 'a' ])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_exp_parse_or(self):
        env = mlisp.Environment(bindings=[('a', mlisp.VNumber(42))])
        # empty
        inp = _make_sexp(['or'])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        # many
        inp = _make_sexp(['or', 'a'])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        inp = _make_sexp(['or', '1', 'a' ])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 1)
        inp = _make_sexp(['or', '0', '2', 'a' ])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 2)
        inp = _make_sexp(['or', '0', '0', 'a' ])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        inp = _make_sexp(['or', '0', '#f', '0' ])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 0)


    def test_exp_parse_loop(self):
        env = mlisp.Environment(bindings=[('a', mlisp.VNumber(42)),
                                         ('=', mlisp.VPrimitive('=', mlisp.prim_numequal, 2)),
                                         ('+', mlisp.VPrimitive('+', mlisp.prim_plus, 2))])
        inp = _make_sexp(['loop', 's', [['n', 'a'], ['sum', '0']],
                          ['if', ['=', 'n', '0'], 'sum',
                           ['s', ['+', 'n', '-1'], ['+', 'sum', 'n']]]])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 903)


    def test_exp_parse_funrec(self):
        env = mlisp.Environment(bindings=[('a', mlisp.VNumber(42)),
                                         ('=', mlisp.VPrimitive('=', mlisp.prim_numequal, 2)),
                                         ('+', mlisp.VPrimitive('+', mlisp.prim_plus, 2))])
        inp = _make_sexp([['funrec', 's', ['n', 'sum'],
                           ['if', ['=', 'n', '0'], 'sum',
                            ['s', ['+', 'n', '-1'], ['+', 'sum', 'n']]]], 'a', '0'])
        e = mlisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 903)


#
# Declarations
#

class TestDeclarationParsing(TestCase):

    def test_parse_define(self):
        env = mlisp.Environment()
        inp = _make_sexp(['def', 'A', '42'])
        p = mlisp.Parser().parse_define(inp)
        self.assertEqual(type(p), type((1, 2)))
        self.assertEqual(p[0], 'a')
        v = p[1].eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)

    def test_parse_defun(self):
        env = mlisp.Environment(bindings=[('a', mlisp.VNumber(42))])
        inp = _make_sexp(['def', ['FOO', 'A', 'B'], 'a'])
        p = mlisp.Parser().parse_defun(inp)
        self.assertEqual(type(p), type((1, 2)))
        self.assertEqual(p[0], 'foo')
        self.assertEqual(p[1], ['a', 'b'])
        v = p[2].eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_parse_decl_define(self):
        env = mlisp.Environment()
        inp = _make_sexp(['def', 'A', '42'])
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
        inp = _make_sexp(['def', ['FOO', 'A', 'B'], 'a'])
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
        inp = _make_sexp('42')
        r = mlisp.Parser().parse(inp)
        self.assertEqual(type(r), type((1, 2)))
        self.assertEqual(r[0], 'exp')
        p = r[1]
        v = p.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # lambda
        inp = _make_sexp(['fn', ['a', 'b'], 'a'])
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
        v = mlisp.prim_type([mlisp.VBoolean(True)])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'boolean')
        v = mlisp.prim_type([mlisp.VString('Alice')])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'string')
        v = mlisp.prim_type([mlisp.VNumber(42)])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'number')
        v = mlisp.prim_type([mlisp.VReference(mlisp.VNumber(42))])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'ref')
        v = mlisp.prim_type([mlisp.VNil()])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'nil')
        v = mlisp.prim_type([mlisp.VEmpty()])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'empty-list')
        v = mlisp.prim_type([mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'cons-list')
        def prim (args):
            return (args[0], args[1])
        v = mlisp.prim_type([mlisp.VPrimitive('prim', prim, 2)])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'primitive')
        v = mlisp.prim_type([mlisp.VSymbol('Alice')])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'symbol')
        v = mlisp.prim_type([mlisp.VFunction(['a', 'b'], mlisp.Symbol('a'), mlisp.Environment())])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'function')


    def test_prim_plus(self):
        v = mlisp.prim_plus([])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 0)
        v = mlisp.prim_plus([mlisp.VNumber(42)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        v = mlisp.prim_plus([mlisp.VNumber(42), mlisp.VNumber(84)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42 + 84)
        v = mlisp.prim_plus([mlisp.VNumber(42), mlisp.VNumber(84), mlisp.VNumber(168)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42 + 84 + 168)


    def test_prim_times(self):
        v = mlisp.prim_times([])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 1)
        v = mlisp.prim_times([mlisp.VNumber(42)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        v = mlisp.prim_times([mlisp.VNumber(42), mlisp.VNumber(84)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42 * 84)
        v = mlisp.prim_times([mlisp.VNumber(42), mlisp.VNumber(84), mlisp.VNumber(168)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42 * 84 * 168)


    def test_prim_minus(self):
        v = mlisp.prim_minus([mlisp.VNumber(42)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), -42)
        v = mlisp.prim_minus([mlisp.VNumber(42), mlisp.VNumber(84)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42 - 84)
        v = mlisp.prim_minus([mlisp.VNumber(42), mlisp.VNumber(84), mlisp.VNumber(168)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42 - 84 - 168)


    def test_prim_numequal(self):
        v = mlisp.prim_numequal([mlisp.VNumber(0), mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numequal([mlisp.VNumber(42), mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numequal([mlisp.VNumber(0), mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_numequal([mlisp.VNumber(42), mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)


    def test_prim_numless(self):
        v = mlisp.prim_numless([mlisp.VNumber(0), mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_numless([mlisp.VNumber(42), mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numless([mlisp.VNumber(0), mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numless([mlisp.VNumber(42), mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_numlesseq(self):
        v = mlisp.prim_numlesseq([mlisp.VNumber(0), mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_numlesseq([mlisp.VNumber(42), mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numlesseq([mlisp.VNumber(0), mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_numlesseq([mlisp.VNumber(42), mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)


    def test_prim_numgreater(self):
        v = mlisp.prim_numgreater([mlisp.VNumber(0), mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numgreater([mlisp.VNumber(42), mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_numgreater([mlisp.VNumber(0), mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numgreater([mlisp.VNumber(42), mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_numgreatereq(self):
        v = mlisp.prim_numgreatereq([mlisp.VNumber(0), mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numgreatereq([mlisp.VNumber(42), mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_numgreatereq([mlisp.VNumber(0), mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_numgreatereq([mlisp.VNumber(42), mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)


    def test_prim_not(self):
        v = mlisp.prim_not([mlisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_not([mlisp.VBoolean(False)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_not([mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_not([mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_not([mlisp.VString('')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_not([mlisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_not([mlisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_not([mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_string_append(self):
        v = mlisp.prim_string_append([])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '')
        v = mlisp.prim_string_append([mlisp.VString('Alice')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        v = mlisp.prim_string_append([mlisp.VString('Alice'), mlisp.VString('Bob')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'AliceBob')
        v = mlisp.prim_string_append([mlisp.VString('Alice'), mlisp.VString('Bob'), mlisp.VString('Charlie')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'AliceBobCharlie')


    def test_prim_string_length(self):
        v = mlisp.prim_string_length([mlisp.VString('')])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 0)
        v = mlisp.prim_string_length([mlisp.VString('Alice')])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 5)
        v = mlisp.prim_string_length([mlisp.VString('Alice Bob')])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 9)


    def test_prim_string_lower(self):
        v = mlisp.prim_string_lower([mlisp.VString('')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '')
        v = mlisp.prim_string_lower([mlisp.VString('Alice')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'alice')
        v = mlisp.prim_string_lower([mlisp.VString('Alice Bob')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'alice bob')


    def test_prim_string_upper(self):
        v = mlisp.prim_string_upper([mlisp.VString('')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '')
        v = mlisp.prim_string_upper([mlisp.VString('Alice')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'ALICE')
        v = mlisp.prim_string_upper([mlisp.VString('Alice Bob')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'ALICE BOB')


    def test_prim_string_substring(self):
        v = mlisp.prim_string_substring([mlisp.VString('')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '')
        v = mlisp.prim_string_substring([mlisp.VString('Alice')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        v = mlisp.prim_string_substring([mlisp.VString('Alice'), mlisp.VNumber(0)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        v = mlisp.prim_string_substring([mlisp.VString('Alice'), mlisp.VNumber(1)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'lice')
        v = mlisp.prim_string_substring([mlisp.VString('Alice'), mlisp.VNumber(2)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'ice')
        v = mlisp.prim_string_substring([mlisp.VString('Alice'), mlisp.VNumber(0), mlisp.VNumber(5)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        v = mlisp.prim_string_substring([mlisp.VString('Alice'), mlisp.VNumber(0), mlisp.VNumber(3)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Ali')
        v = mlisp.prim_string_substring([mlisp.VString('Alice'), mlisp.VNumber(2), mlisp.VNumber(3)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'i')
        v = mlisp.prim_string_substring([mlisp.VString('Alice'), mlisp.VNumber(0), mlisp.VNumber(0)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '')
        v = mlisp.prim_string_substring([mlisp.VString('Alice'), mlisp.VNumber(3), mlisp.VNumber(3)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '')


    def test_prim_apply(self):
        def prim (args):
            return (args[0], args[1])
        v = mlisp.prim_apply([mlisp.VPrimitive('test', prim, 2, 2),
                             _make_list([mlisp.VNumber(42), mlisp.VString('Alice')])])
        self.assertEqual(v[0].is_number(), True)
        self.assertEqual(v[0].value(), 42)
        self.assertEqual(v[1].is_string(), True)
        self.assertEqual(v[1].value(), 'Alice')
        v = mlisp.prim_apply([mlisp.VFunction(['a', 'b'], mlisp.Symbol('a'), mlisp.Environment()),
                             _make_list([mlisp.VNumber(42), mlisp.VString('Alice')])])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_prim_cons(self):
        v = mlisp.prim_cons([mlisp.VNumber(42), mlisp.VEmpty()])
        l = _unmake_list(v)
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 42)
        v = mlisp.prim_cons([mlisp.VNumber(42), _make_list([mlisp.VString('Alice'), mlisp.VString('Bob')])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 3)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 42)
        self.assertEqual(l[1].is_string(), True)
        self.assertEqual(l[1].value(), 'Alice')
        self.assertEqual(l[2].is_string(), True)
        self.assertEqual(l[2].value(), 'Bob')


    def test_prim_append(self):
        v = mlisp.prim_append([])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = mlisp.prim_append([_make_list([mlisp.VNumber(1), mlisp.VNumber(2)])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 2)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 1)
        self.assertEqual(l[1].is_number(), True)
        self.assertEqual(l[1].value(), 2)
        v = mlisp.prim_append([_make_list([mlisp.VNumber(1), mlisp.VNumber(2)]),
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
        v = mlisp.prim_append([_make_list([mlisp.VNumber(1), mlisp.VNumber(2)]),
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
        v = mlisp.prim_reverse([_make_list([mlisp.VNumber(1),
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
        v = mlisp.prim_first([_make_list([mlisp.VNumber(42)])])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        v = mlisp.prim_first([_make_list([mlisp.VNumber(42),
                                         mlisp.VString('Alice'),
                                         mlisp.VString('Bob')])])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_prim_rest(self):
        v = mlisp.prim_rest([_make_list([mlisp.VNumber(42)])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = mlisp.prim_rest([_make_list([mlisp.VNumber(42),
                                        mlisp.VString('Alice'),
                                        mlisp.VString('Bob')])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 2)
        self.assertEqual(l[0].is_string(), True)
        self.assertEqual(l[0].value(), 'Alice')
        self.assertEqual(l[1].is_string(), True)
        self.assertEqual(l[1].value(), 'Bob')


    def test_prim_list(self):
        v = mlisp.prim_list([])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = mlisp.prim_list([mlisp.VNumber(42)])
        l = _unmake_list(v)
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 42)
        v = mlisp.prim_list([mlisp.VNumber(42),
                            mlisp.VString('Alice')])
        l = _unmake_list(v)
        self.assertEqual(len(l), 2)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 42)
        self.assertEqual(l[1].is_string(), True)
        self.assertEqual(l[1].value(), 'Alice')
        v = mlisp.prim_list([mlisp.VNumber(42),
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
        v = mlisp.prim_length([_make_list([])])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 0)
        v = mlisp.prim_length([_make_list([mlisp.VNumber(42)])])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 1)
        v = mlisp.prim_length([_make_list([mlisp.VNumber(42),
                                          mlisp.VString('Alice')])])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 2)
        v = mlisp.prim_length([_make_list([mlisp.VNumber(42),
                                          mlisp.VString('Alice'),
                                          mlisp.VString('Bob')])])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 3)


    def test_prim_nth(self):
        v = mlisp.prim_nth([_make_list([mlisp.VNumber(42),
                                       mlisp.VString('Alice'),
                                       mlisp.VString('Bob')]),
                           mlisp.VNumber(0)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        v = mlisp.prim_nth([_make_list([mlisp.VNumber(42),
                                       mlisp.VString('Alice'),
                                       mlisp.VString('Bob')]),
                           mlisp.VNumber(1)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        v = mlisp.prim_nth([_make_list([mlisp.VNumber(42),
                                       mlisp.VString('Alice'),
                                       mlisp.VString('Bob')]),
                           mlisp.VNumber(2)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Bob')


    def test_prim_map(self):
        def prim1 (args):
            return args[0]
        def prim2 (args):
            return args[1]
        v = mlisp.prim_map([mlisp.VPrimitive('test', prim1, 1),
                           _make_list([])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = mlisp.prim_map([mlisp.VPrimitive('test', prim1, 1),
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
        v = mlisp.prim_map([mlisp.VPrimitive('test', prim2, 2),
                           _make_list([]),
                           _make_list([])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = mlisp.prim_map([mlisp.VPrimitive('test', prim2, 2),
                           _make_list([]),
                           _make_list([mlisp.VNumber(42)])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = mlisp.prim_map([mlisp.VPrimitive('test', prim2, 2),
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
        def prim_none (args):
            return mlisp.VBoolean(False)
        def prim_int (args):
            return mlisp.VBoolean(args[0].is_number())
        v = mlisp.prim_filter([mlisp.VPrimitive('test', prim_none, 1),
                              _make_list([])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = mlisp.prim_filter([mlisp.VPrimitive('test', prim_none, 1),
                              _make_list([mlisp.VNumber(42),
                                          mlisp.VString('Alice'),
                                          mlisp.VString('Bob')])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = mlisp.prim_filter([mlisp.VPrimitive('test', prim_int, 1),
                              _make_list([mlisp.VNumber(42),
                                          mlisp.VString('Alice'),
                                          mlisp.VString('Bob')])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 42)


    def test_prim_foldr(self):
        def prim (args):
            return mlisp.VString(args[0].value() + '(' + args[1].value() + ')')
        v = mlisp.prim_foldr([mlisp.VPrimitive('test', prim, 2),
                             _make_list([]),
                             mlisp.VString('base')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'base')
        v = mlisp.prim_foldr([mlisp.VPrimitive('test', prim, 2),
                             _make_list([mlisp.VString('Alice'),
                                         mlisp.VString('Bob'),
                                         mlisp.VString('Charlie')]),
                             mlisp.VString('base')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice(Bob(Charlie(base)))')


    def test_prim_foldl(self):
        def prim (args):
            return mlisp.VString('(' + args[0].value() + ')' + args[1].value())
        v = mlisp.prim_foldl([mlisp.VPrimitive('test', prim, 2),
                             mlisp.VString('base'),
                             _make_list([])])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'base')
        v = mlisp.prim_foldl([mlisp.VPrimitive('test', prim, 2),
                             mlisp.VString('base'),
                             _make_list([mlisp.VString('Alice'),
                                         mlisp.VString('Bob'),
                                         mlisp.VString('Charlie')])])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '(((base)Alice)Bob)Charlie')


    def test_prim_eqp(self):
        v = mlisp.prim_eqp([mlisp.VNumber(42),
                           mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_eqp([mlisp.VNumber(42),
                           mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        lst = _make_list([mlisp.VNumber(42)])
        v = mlisp.prim_eqp([lst, lst])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_eqp([lst, _make_list([mlisp.VNumber(42)])])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_eqp([lst, mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_eqp([lst, _make_list([mlisp.VNumber(84)])])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_eqlp(self):
        v = mlisp.prim_eqlp([mlisp.VNumber(42),
                           mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_eqlp([mlisp.VNumber(42),
                           mlisp.VNumber(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        lst = _make_list([mlisp.VNumber(42)])
        v = mlisp.prim_eqlp([lst, lst])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_eqlp([lst, _make_list([mlisp.VNumber(42)])])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_eqlp([lst, mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_eqlp([lst, _make_list([mlisp.VNumber(84)])])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        ref = mlisp.VReference(mlisp.VNumber(42))
        v = mlisp.prim_eqlp([ref, ref])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_eqlp([ref, mlisp.VReference(mlisp.VNumber(42))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_eqlp([ref, mlisp.VReference(mlisp.VNumber(0))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_emptyp(self):
        v = mlisp.prim_emptyp([mlisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_emptyp([mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_emptyp([mlisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_emptyp([mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_emptyp([mlisp.VReference(mlisp.VNumber(42))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_emptyp([mlisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_emptyp([mlisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_emptyp([mlisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_emptyp([mlisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_emptyp([mlisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = mlisp.prim_emptyp([mlisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_emptyp([mlisp.VFunction(['a'], mlisp.VSymbol('a'), mlisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_consp(self):
        v = mlisp.prim_consp([mlisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_consp([mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_consp([mlisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_consp([mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_consp([mlisp.VReference(mlisp.VNumber(42))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_consp([mlisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_consp([mlisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_consp([mlisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_consp([mlisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_consp([mlisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = mlisp.prim_consp([mlisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_consp([mlisp.VFunction(['a'], mlisp.VSymbol('a'), mlisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_listp(self):
        v = mlisp.prim_listp([mlisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_listp([mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_listp([mlisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_listp([mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_listp([mlisp.VReference(mlisp.VNumber(42))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_listp([mlisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_listp([mlisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_listp([mlisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_listp([mlisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_listp([mlisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = mlisp.prim_listp([mlisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_listp([mlisp.VFunction(['a'], mlisp.VSymbol('a'), mlisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_numberp(self):
        v = mlisp.prim_numberp([mlisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numberp([mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numberp([mlisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numberp([mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_numberp([mlisp.VReference(mlisp.VNumber(42))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numberp([mlisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numberp([mlisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numberp([mlisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numberp([mlisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numberp([mlisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = mlisp.prim_numberp([mlisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_numberp([mlisp.VFunction(['a'], mlisp.VSymbol('a'), mlisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_booleanp(self):
        v = mlisp.prim_booleanp([mlisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_booleanp([mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_booleanp([mlisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_booleanp([mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_booleanp([mlisp.VReference(mlisp.VNumber(42))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_booleanp([mlisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_booleanp([mlisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_booleanp([mlisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_booleanp([mlisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_booleanp([mlisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = mlisp.prim_booleanp([mlisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_booleanp([mlisp.VFunction(['a'], mlisp.VSymbol('a'), mlisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_stringp(self):
        v = mlisp.prim_stringp([mlisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_stringp([mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_stringp([mlisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_stringp([mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_stringp([mlisp.VReference(mlisp.VNumber(42))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_stringp([mlisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_stringp([mlisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_stringp([mlisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_stringp([mlisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_stringp([mlisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = mlisp.prim_stringp([mlisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_stringp([mlisp.VFunction(['a'], mlisp.VSymbol('a'), mlisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_symbolp(self):
        v = mlisp.prim_symbolp([mlisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_symbolp([mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_symbolp([mlisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_symbolp([mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_symbolp([mlisp.VReference(mlisp.VNumber(42))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_symbolp([mlisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_symbolp([mlisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_symbolp([mlisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_symbolp([mlisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_symbolp([mlisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = mlisp.prim_symbolp([mlisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_symbolp([mlisp.VFunction(['a'], mlisp.VSymbol('a'), mlisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_functionp(self):
        v = mlisp.prim_functionp([mlisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_functionp([mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_functionp([mlisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_functionp([mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_functionp([mlisp.VReference(mlisp.VNumber(42))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_functionp([mlisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_functionp([mlisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_functionp([mlisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_functionp([mlisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_functionp([mlisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = mlisp.prim_functionp([mlisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_functionp([mlisp.VFunction(['a'], mlisp.VSymbol('a'), mlisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)


    def test_prim_nilp(self):
        v = mlisp.prim_nilp([mlisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_nilp([mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_nilp([mlisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_nilp([mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_nilp([mlisp.VReference(mlisp.VNumber(42))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_nilp([mlisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_nilp([mlisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_nilp([mlisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_nilp([mlisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_nilp([mlisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True )
        v = mlisp.prim_nilp([mlisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_nilp([mlisp.VFunction(['a'], mlisp.VSymbol('a'), mlisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_refp(self):
        v = mlisp.prim_refp([mlisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_refp([mlisp.VCons(mlisp.VNumber(42), mlisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_refp([mlisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_refp([mlisp.VNumber(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_refp([mlisp.VReference(mlisp.VNumber(42))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = mlisp.prim_refp([mlisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_refp([mlisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_refp([mlisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_refp([mlisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_refp([mlisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_refp([mlisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = mlisp.prim_refp([mlisp.VFunction(['a'], mlisp.VSymbol('a'), mlisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_ref(self):
        val = mlisp.VNumber(42)
        v = mlisp.prim_ref([val])
        self.assertEqual(v.is_reference(), True)
        self.assertEqual(v.value(), val)
        val = mlisp.VString("Alice")
        v = mlisp.prim_ref([val])
        self.assertEqual(v.is_reference(), True)
        self.assertEqual(v.value(), val)
        val = mlisp.VReference(mlisp.VNumber(42))
        v = mlisp.prim_ref([val])
        self.assertEqual(v.is_reference(), True)
        self.assertEqual(v.value(), val)


    def test_prim_ref_get(self):
        val = mlisp.VReference(mlisp.VNumber(42))
        v = mlisp.prim_ref_get([val])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        val = mlisp.VReference(mlisp.VString("Alice"))
        v = mlisp.prim_ref_get([val])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), "Alice")
        val = mlisp.VReference(mlisp.VReference(mlisp.VNumber(42)))
        v = mlisp.prim_ref_get([val])
        self.assertEqual(v.is_reference(), True)
        self.assertEqual(v.value().is_number(), True)
        self.assertEqual(v.value().value(), 42)


    def test_prim_ref_set(self):
        val = mlisp.VReference(mlisp.VNumber(0))
        v = mlisp.prim_ref_set([val, mlisp.VNumber(42)])
        self.assertEqual(v.is_nil(), True)
        self.assertEqual(val.value().is_number(), True)
        self.assertEqual(val.value().value(), 42)
        val = mlisp.VReference(mlisp.VNumber(0))
        v = mlisp.prim_ref_set([val, mlisp.VString("Alice")])
        self.assertEqual(v.is_nil(), True)
        self.assertEqual(val.value().is_string(), True)
        self.assertEqual(val.value().value(), "Alice")
        val = mlisp.VReference(mlisp.VNumber(0))
        v = mlisp.prim_ref_set([val, mlisp.VReference(mlisp.VNumber(42))])
        self.assertEqual(v.is_nil(), True)
        self.assertEqual(val.value().is_reference(), True)
        self.assertEqual(val.value().value().is_number(), True)
        self.assertEqual(val.value().value().value(), 42)
    
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
        self.assertEqual(s.content(), '42')
        self.assertEqual(s.as_value().is_number(), True)
        self.assertEqual(s.as_value().value(), 42)
        # cons
        inp = '(42 Alice Bob)'
        s = engine.read(inp)
        self.assertEqual(s.is_atom(), False)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), True)
        self.assertEqual(s.as_value().is_cons(), True)
        self.assertEqual(s.as_value().car().is_number(), True)
        self.assertEqual(s.as_value().car().value(), 42)
        self.assertEqual(s.as_value().cdr().is_cons(), True)
        self.assertEqual(s.as_value().cdr().car().is_symbol(), True)
        self.assertEqual(s.as_value().cdr().car().value(), 'alice')
        self.assertEqual(s.as_value().cdr().cdr().is_cons(), True)
        self.assertEqual(s.as_value().cdr().cdr().car().is_symbol(), True)
        self.assertEqual(s.as_value().cdr().cdr().car().value(), 'bob')
        self.assertEqual(s.as_value().cdr().cdr().cdr().is_empty(), True)


    def test_engine_eval_sexp(self):
        # integer
        engine = mlisp.Engine()
        inp = _make_sexp('42')
        v = engine.eval_sexp(inp)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # application
        engine = mlisp.Engine()
        inp = _make_sexp([['fn', ['a', 'b'], 'a'], '42', '0'])
        v = engine.eval_sexp(inp)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # define
        engine = mlisp.Engine()
        inp = _make_sexp(['def', 'a', '42'])
        engine.eval_sexp(inp)
        v = engine.eval_sexp(_make_sexp('a'))
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # defun
        engine = mlisp.Engine()
        inp = _make_sexp(['def', ['foo', 'a'], 'a'])
        engine.eval_sexp(inp)
        v = engine.eval_sexp(_make_sexp(['foo', '42']))
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_engine_eval(self):
        # integer
        engine = mlisp.Engine()
        inp = '42'
        v = engine.eval(inp)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # application
        engine = mlisp.Engine()
        inp = '((fn (a b) a) 42 0)'
        v = engine.eval(inp)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # define
        engine = mlisp.Engine()
        inp = '(def a 42)'
        engine.eval(inp)
        v = engine.eval('a')
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # defun
        engine = mlisp.Engine()
        inp = '(def (foo a) a)'
        engine.eval(inp)
        v = engine.eval('(foo 42)')
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_engine_bindings(self):
        # no init bindings
        engine = mlisp.Engine()
        v = engine.eval('type')
        self.assertEqual(v.is_function(), True)
        v = engine.eval('empty')
        self.assertEqual(v.is_empty(), True)
        # init bindings
        engine = mlisp.Engine(bindings=[('a', mlisp.VNumber(42)), ('b', mlisp.VString('Alice'))])
        v = engine.eval('a')
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        v = engine.eval('b')
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')


    def test_engine_add_env(self):
        # no init bindings
        engine = mlisp.Engine()
        engine.add_env([('a', mlisp.VNumber(42)), ('b', mlisp.VString('Alice'))])
        v = engine.eval('a')
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        v = engine.eval('empty')
        self.assertEqual(v.is_empty(), True)
        # init bindings
        engine = mlisp.Engine(bindings=[('x', mlisp.VNumber(42)), ('y', mlisp.VString('Alice'))])
        engine.add_env([('a', mlisp.VNumber(42)), ('b', mlisp.VString('Alice'))])
        v = engine.eval('a')
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        v = engine.eval('b')
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        v = engine.eval('empty')
        self.assertEqual(v.is_empty(), True)
        v = engine.eval('y')
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
    
    
