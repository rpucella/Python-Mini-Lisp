from unittest import TestCase

import lisp

# TODO - share testing function between the various pieces that have commonality
#  e.g., parse_sexp_int <- used to test both parse_sexp() and to test engine.read()


def _make_sexp(struct):
    if type(struct) == type([]):
        result = lisp.SEmpty()
        for r in reversed(struct):
            result = lisp.SCons(_make_sexp(r), result)
        return result
    else:
        return lisp.SAtom(struct)

    
def _make_list (struct):
    if type(struct) == type([]):
        result = lisp.VEmpty()
        for r in reversed(struct):
            result = lisp.VCons(_make_list(r), result)
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
        e = lisp.Environment()
        e.add('Alice', 42)
        self.assertEqual(e.lookup('alice'), 42)
        self.assertEqual(e.lookup('ALICE'), 42)
        self.assertEqual(list(e.bindings()), [('alice',42)], 'bindings')
        self.assertEqual(e.previous(), None)

    def test_initial(self):
        # initial bindings
        e = lisp.Environment(bindings=[('Alice', 42), ('Bob', 84)])
        self.assertEqual(e.lookup('ALICE'), 42)
        self.assertEqual(e.lookup('BOB'), 84)
        self.assertEqual(list(e.bindings()), [('alice',42), ('bob', 84)])
        self.assertEqual(e.previous(), None)

    def test_linked(self):
        # linked environments
        e = lisp.Environment(bindings=[('alice', 42)])
        e2 = lisp.Environment(bindings=[('bob', 84)], previous=e)
        self.assertEqual(e2.lookup('alice'), 42)
        self.assertEqual(e2.lookup('bob'), 84)
        self.assertEqual(e2.previous(), e)

    def test_overwrites(self):
        # add overwrites existing
        e = lisp.Environment(bindings=[('Alice', 42)])
        e.add('Alice', 84)
        self.assertEqual(list(e.bindings()), [('alice', 84)])
        e2 = lisp.Environment(previous=e)
        e2.add('Alice', 42)
        self.assertEqual(list(e2.bindings()), [('alice', 42)])
        self.assertEqual(list(e2.previous().bindings()), [('alice', 84)])

    def test_updates(self):
        # updates
        e = lisp.Environment(bindings=[('Alice', 42), ('Bob', 84)])
        e.update('Alice', 168)
        self.assertEqual(list(e.bindings()), [('alice', 168), ('bob', 84)])
        e = lisp.Environment(bindings=[('Alice', 42)])
        e2 = lisp.Environment(bindings=[('Bob', 84)], previous=e)
        e2.update('Alice', 168)
        self.assertEqual(list(e2.bindings()), [('bob', 84)])
        self.assertEqual(list(e2.previous().bindings()), [('alice', 168)])


class TestValueBoolean(TestCase):

    def test_true(self):
        # True
        b = lisp.VBoolean(True)
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
        self.assertEqual(b.is_equal(lisp.VBoolean(True)), True)
        self.assertEqual(b.is_equal(lisp.VBoolean(False)), False)
        self.assertEqual(b.is_equal(lisp.VInteger(42)), False)
        self.assertEqual(b.is_eq(lisp.VBoolean(True)), True)
        self.assertEqual(b.is_eq(lisp.VBoolean(False)), False)
        self.assertEqual(b.is_eq(lisp.VInteger(42)), False)
        self.assertEqual(b.value(), True)

    def test_false(self):
        b = lisp.VBoolean(False)
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
        self.assertEqual(b.is_equal(lisp.VBoolean(True)), False)
        self.assertEqual(b.is_equal(lisp.VBoolean(False)), True)
        self.assertEqual(b.is_equal(lisp.VInteger(42)), False)
        self.assertEqual(b.is_eq(lisp.VBoolean(True)), False)
        self.assertEqual(b.is_eq(lisp.VBoolean(False)), True)
        self.assertEqual(b.is_eq(lisp.VInteger(42)), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertEqual(b.value(), False)
    

class TestValueString(TestCase):
    
    def test_empty(self):
        # empty
        b = lisp.VString('')
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
        self.assertEqual(b.is_equal(lisp.VString('')), True)
        self.assertEqual(b.is_equal(lisp.VString('Alice')), False)
        self.assertEqual(b.is_equal(lisp.VInteger(42)), False)
        self.assertEqual(b.is_eq(lisp.VString('')), False)
        self.assertEqual(b.is_eq(lisp.VString('Alice')), False)
        self.assertEqual(b.is_eq(lisp.VInteger(42)), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertEqual(b.value(), '')

    def test_non_empty(self):
        # non-empty
        b = lisp.VString('Alice')
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
        self.assertEqual(b.is_equal(lisp.VString('')), False)
        self.assertEqual(b.is_equal(lisp.VString('Alice')), True)
        self.assertEqual(b.is_equal(lisp.VInteger(42)), False)
        self.assertEqual(b.is_eq(lisp.VString('')), False)
        self.assertEqual(b.is_eq(lisp.VString('Alice')), False)
        self.assertEqual(b.is_eq(lisp.VInteger(42)), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertEqual(b.value(), 'Alice')

    def test_special(self):
        # special characters
        b = lisp.VString('\\t\\n\\"')
        self.assertEqual(str(b), '"\\t\\n\\""')
        self.assertEqual(b.display(), '\t\n"')
        # accented characters
        b = lisp.VString('\u00e9\u00ea\00e8')
        self.assertEqual(str(b), '"\u00e9\u00ea\00e8"')
        self.assertEqual(b.display(), '\u00e9\u00ea\00e8')


class TestValueInteger(TestCase):

    def test_zero(self):
        # zero
        b = lisp.VInteger(0)
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
        self.assertEqual(b.is_equal(lisp.VInteger(0)), True)
        self.assertEqual(b.is_equal(lisp.VInteger(42)), False)
        self.assertEqual(b.is_equal(lisp.VString('Alice')), False)
        self.assertEqual(b.is_eq(lisp.VInteger(0)), True)
        self.assertEqual(b.is_eq(lisp.VInteger(42)), False)
        self.assertEqual(b.is_eq(lisp.VString('Alice')), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertEqual(b.value(), 0)

    def test_non_zero(self):
        # non-zero
        b = lisp.VInteger(42)
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
        self.assertEqual(b.is_equal(lisp.VInteger(0)), False)
        self.assertEqual(b.is_equal(lisp.VInteger(42)), True)
        self.assertEqual(b.is_equal(lisp.VString('Alice')), False)
        self.assertEqual(b.is_eq(lisp.VInteger(0)), False)
        self.assertEqual(b.is_eq(lisp.VInteger(42)), True)
        self.assertEqual(b.is_eq(lisp.VString('Alice')), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertEqual(b.value(), 42)


class TestValueNil(TestCase):

    def test_nil(self):
        b = lisp.VNil()
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
        self.assertEqual(b.is_equal(lisp.VNil()), True)
        self.assertEqual(b.is_equal(lisp.VInteger(42)), False)
        self.assertEqual(b.is_eq(lisp.VNil()), True)
        self.assertEqual(b.is_eq(lisp.VInteger(42)), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertIs(b.value(), None)


class TestValueReference(TestCase):

    def test_num(self):
        # num
        val = lisp.VInteger(42)
        r = lisp.VReference(val)
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
        self.assertEqual(r.is_equal(lisp.VReference(val)), True)
        self.assertEqual(r.is_equal(lisp.VReference(lisp.VInteger(42))), True)
        self.assertEqual(r.is_equal(lisp.VReference(lisp.VInteger(0))), False)
        self.assertEqual(r.is_equal(lisp.VReference(lisp.VString("Alice"))), False)
        self.assertEqual(r.is_eq(lisp.VReference(val)), False)
        self.assertEqual(r.is_eq(lisp.VReference(lisp.VInteger(42))), False)
        self.assertEqual(r.is_eq(lisp.VReference(lisp.VInteger(0))), False)
        self.assertEqual(r.is_eq(lisp.VReference(lisp.VString("Alice"))), False)
        self.assertEqual(r.is_equal(r), True)
        self.assertEqual(r.is_eq(r), True)
        self.assertEqual(r.value(), val)

    def test_string(self):
        # string
        val = lisp.VString("Alice")
        r = lisp.VReference(val)
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
        self.assertEqual(r.is_equal(lisp.VReference(lisp.VInteger(42))), False)
        self.assertEqual(r.is_equal(lisp.VReference(val)), True)
        self.assertEqual(r.is_equal(lisp.VReference(lisp.VString("Alice"))), True)
        self.assertEqual(r.is_equal(lisp.VReference(lisp.VString("Bob"))), False)
        self.assertEqual(r.is_eq(lisp.VReference(lisp.VInteger(42))), False)
        self.assertEqual(r.is_eq(lisp.VReference(val)), False)
        self.assertEqual(r.is_eq(lisp.VReference(lisp.VString("Alice"))), False)
        self.assertEqual(r.is_eq(lisp.VReference(lisp.VString("Bob"))), False)
        self.assertEqual(r.is_equal(r), True)
        self.assertEqual(r.is_eq(r), True)
        self.assertEqual(r.value(), val)

    def test_nested(self):
        # nested
        val = lisp.VReference(lisp.VInteger(42))
        r = lisp.VReference(val)
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
        self.assertEqual(r.is_equal(lisp.VReference(val)), True)
        self.assertEqual(r.is_equal(lisp.VReference(lisp.VReference(lisp.VInteger(42)))), True)
        self.assertEqual(r.is_equal(lisp.VReference(lisp.VInteger(42))), False)
        self.assertEqual(r.is_eq(lisp.VReference(val)), False)
        self.assertEqual(r.is_eq(lisp.VReference(lisp.VReference(lisp.VInteger(42)))), False)
        self.assertEqual(r.is_eq(lisp.VReference(lisp.VInteger(42))), False)
        self.assertEqual(r.is_equal(r), True)
        self.assertEqual(r.is_eq(r), True)
        self.assertEqual(r.value(), val)
    

class TestValueEmpty(TestCase):
    
    def test_empty(self):
        b = lisp.VEmpty()
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
        self.assertEqual(b.is_equal(lisp.VEmpty()), True)
        self.assertEqual(b.is_equal(lisp.VCons(lisp.VInteger(42), lisp.VEmpty())), False)
        self.assertEqual(b.is_equal(lisp.VInteger(42)), False)
        self.assertEqual(b.is_eq(lisp.VEmpty()), True)
        self.assertEqual(b.is_eq(lisp.VCons(lisp.VInteger(42), lisp.VEmpty())), False)
        self.assertEqual(b.is_eq(lisp.VInteger(42)), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertEqual(b.value() is None, True)
        self.assertEqual(b.to_list(), [])


class TestValueCons(TestCase):
    
    def test_cons_1(self):
        car = lisp.VInteger(42)
        cdr = lisp.VEmpty()
        b = lisp.VCons(car, cdr)
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
        self.assertEqual(b.is_equal(lisp.VEmpty()), False)
        self.assertEqual(b.is_equal(lisp.VCons(lisp.VInteger(42), lisp.VEmpty())), True)
        self.assertEqual(b.is_equal(lisp.VInteger(42)), False)
        self.assertEqual(b.is_eq(lisp.VEmpty()), False)
        self.assertEqual(b.is_eq(lisp.VCons(lisp.VInteger(42), lisp.VEmpty())), False)
        self.assertEqual(b.is_eq(lisp.VInteger(42)), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertEqual(b.value(), (car, cdr))
        self.assertEqual(b.to_list(), [car])
        self.assertEqual(b.car(), car)
        self.assertEqual(b.cdr(), cdr)

    def test_cons_2(self):
        car = lisp.VInteger(42)
        cadr = lisp.VInteger(84)
        cddr = lisp.VEmpty()
        c = lisp.VCons(cadr, cddr)
        b = lisp.VCons(car, c)
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
        self.assertEqual(b.is_equal(lisp.VEmpty()), False)
        self.assertEqual(b.is_equal(lisp.VCons(lisp.VInteger(42), lisp.VEmpty())), False)
        self.assertEqual(b.is_equal(lisp.VCons(lisp.VInteger(42), lisp.VCons(lisp.VInteger(84), lisp.VEmpty()))), True)
        self.assertEqual(b.is_equal(lisp.VInteger(42)), False)
        self.assertEqual(b.is_eq(lisp.VEmpty()), False)
        self.assertEqual(b.is_eq(lisp.VCons(lisp.VInteger(42), lisp.VEmpty())), False)
        self.assertEqual(b.is_eq(lisp.VCons(lisp.VInteger(42), lisp.VCons(lisp.VInteger(84), lisp.VEmpty()))), False)
        self.assertEqual(b.is_eq(lisp.VCons(lisp.VInteger(42), c)), False)
        self.assertEqual(b.is_eq(lisp.VInteger(42)), False)
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
        i = lisp.VInteger(42)
        j = lisp.VInteger(0)
        b = lisp.VPrimitive('test', prim, 2)
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
        self.assertEqual(b.is_equal(lisp.VPrimitive('test', prim, 2)), False)
        self.assertEqual(b.is_equal(lisp.VPrimitive('test', lambda args: 0, 2)), False)
        self.assertEqual(b.is_equal(lisp.VInteger(42)), False)
        self.assertEqual(b.is_eq(lisp.VPrimitive('test', prim, 2)), False)
        self.assertEqual(b.is_equal(lisp.VPrimitive('test2', lambda args: 0, 2)), False)
        self.assertEqual(b.is_equal(lisp.VInteger(42)), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertEqual(b.value(), prim)
        self.assertEqual(b.apply([i, j]), (i, j))


class TestValueSymbol(TestCase):
    
    def test_symbol(self):
        b = lisp.VSymbol('Alice')
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
        self.assertEqual(b.is_equal(lisp.VSymbol('Alice')), True)
        self.assertEqual(b.is_equal(lisp.VSymbol('alice')), True)
        self.assertEqual(b.is_equal(lisp.VSymbol('Bob')), False)
        self.assertEqual(b.is_equal(lisp.VInteger(42)), False)
        self.assertEqual(b.is_eq(lisp.VSymbol('Alice')), True)
        self.assertEqual(b.is_eq(lisp.VSymbol('alice')), True)
        self.assertEqual(b.is_eq(lisp.VSymbol('Bob')), False)
        self.assertEqual(b.is_eq(lisp.VInteger(42)), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertEqual(b.value() == 'alice', True)
        # accents
        b = lisp.VSymbol('Test\u00c9')
        self.assertEqual(str(b), 'test\u00e9')
        self.assertEqual(b.display(), 'test\u00e9')
        self.assertEqual(b.value(), 'test\u00e9')
    

class TestValueFunction(TestCase):
    
    def test_no_args(self):
        # no arguments
        i = lisp.Integer(42)
        e = lisp.Environment()
        b = lisp.VFunction([], i, e)
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
        self.assertEqual(b.is_equal(lisp.VFunction([], lisp.Integer(42), lisp.Environment())), False)
        self.assertEqual(b.is_equal(lisp.VFunction([], lisp.Integer(84), lisp.Environment())), False)
        self.assertEqual(b.is_equal(lisp.VInteger(42)), False)
        self.assertEqual(b.is_eq(lisp.VFunction([], lisp.Integer(42), lisp.Environment())), False)
        self.assertEqual(b.is_eq(lisp.VFunction([], lisp.Integer(84), lisp.Environment())), False)
        self.assertEqual(b.is_eq(lisp.VInteger(42)), False)
        self.assertEqual(b.is_equal(b), True)
        self.assertEqual(b.is_eq(b), True)
        self.assertEqual(b.value(), ([], i, e))
        result = b.apply([])
        self.assertEqual(result.is_number(), True)
        self.assertEqual(result.value(), 42)

    def test_2_args(self):
        # 2 arguments
        i = lisp.Integer(42)
        e = lisp.Environment()
        b = lisp.VFunction(['x', 'y'], i, e)
        self.assertEqual(b.value(), (['x', 'y'], i, e))
        result = b.apply([lisp.VInteger(0), lisp.VInteger(0)])
        self.assertEqual(result.is_number(), True)
        self.assertEqual(result.value(), 42)

    def test_2_args_1_used(self):
        # 2 arguments, one used
        i = lisp.Symbol('x')
        e = lisp.Environment()
        b = lisp.VFunction(['x', 'y'], i, e)
        self.assertEqual(b.value(), (['x', 'y'], i, e))
        result = b.apply([lisp.VInteger(42), lisp.VInteger(0)])
        self.assertEqual(result.is_number(), True)
        self.assertEqual(result.value(), 42)

    def test_2_args_env(self):
        # 2 arguments, using environment
        i = lisp.Symbol('z')
        e = lisp.Environment(bindings=[('z', lisp.VInteger(42))])
        b = lisp.VFunction(['x', 'y'], i, e)
        self.assertEqual(b.value(), (['x', 'y'], i, e))
        result = b.apply([lisp.VInteger(0), lisp.VInteger(0)])
        self.assertEqual(result.is_number(), True)
        self.assertEqual(result.value(), 42)


#
# SExpressions
#

class TestSExp(TestCase):
    
    def test_symbol(self):
        s = lisp.SAtom('Alice')
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.content(), 'Alice')
        self.assertEqual(s.as_value().is_symbol(), True)
        self.assertEqual(s.as_value().value(), 'alice')
        # accents
        s = lisp.SAtom('TEST\u00c9')
        self.assertEqual(s.content(), 'TEST\u00c9')
        self.assertEqual(s.as_value().value(), 'test\u00e9')


    def test_string(self):
        s = lisp.SAtom('"Alice"')
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.content(), '"Alice"')
        self.assertEqual(s.as_value().is_string(), True)
        self.assertEqual(s.as_value().value(), 'Alice')
        # accents
        s = lisp.SAtom('"Test\u00e9"')
        self.assertEqual(s.content(), '"Test\u00e9"')
        self.assertEqual(s.as_value().value(), 'Test\u00e9')


    def test_integer(self):
        s = lisp.SAtom('42')
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.content(), '42')
        self.assertEqual(s.as_value().is_number(), True)
        self.assertEqual(s.as_value().value(), 42)


    def test_boolean(self):
        s = lisp.SAtom('#t')
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.content(), '#t')
        self.assertEqual(s.as_value().is_boolean(), True)
        self.assertEqual(s.as_value().value(), True)
        s = lisp.SAtom('#f')
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.content(), '#f')
        self.assertEqual(s.as_value().is_boolean(), True)
        self.assertEqual(s.as_value().value(), False)


    def test_empty(self):
        s = lisp.SEmpty()
        self.assertEqual(s.is_atom(), False)
        self.assertEqual(s.is_empty(), True)
        self.assertEqual(s.is_cons(), False)
        self.assertIs(s.content(), None)
        self.assertEqual(s.as_value().is_empty(), True)


    def test_cons(self):
        car = lisp.SAtom('42')
        cdr = lisp.SEmpty()
        s = lisp.SCons(car, cdr)
        self.assertEqual(s.is_atom(), False)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), True)
        self.assertEqual(s.content(), (car, cdr))
        self.assertEqual(s.as_value().is_cons(), True)
        self.assertEqual(s.as_value().car().is_number(), True)
        self.assertEqual(s.as_value().car().value(), 42)
        self.assertEqual(s.as_value().cdr().is_empty(), True)
    
    def test_from_value(self):
        v = lisp.VBoolean(True)
        self.assertEqual(lisp.SExpression.from_value(v).is_atom(), True)
        self.assertEqual(lisp.SExpression.from_value(v).content(), '#true')
        v = lisp.VBoolean(False)
        self.assertEqual(lisp.SExpression.from_value(v).is_atom(), True)
        self.assertEqual(lisp.SExpression.from_value(v).content(), '#false')
        v = lisp.VString('Alice')
        self.assertEqual(lisp.SExpression.from_value(v).is_atom(), True)
        self.assertEqual(lisp.SExpression.from_value(v).content(), '"Alice"')
        v = lisp.VString('Test\u00e9')
        self.assertEqual(lisp.SExpression.from_value(v).is_atom(), True)
        self.assertEqual(lisp.SExpression.from_value(v).content(), '"Test\u00e9"')
        v = lisp.VInteger(42)
        self.assertEqual(lisp.SExpression.from_value(v).is_atom(), True)
        self.assertEqual(lisp.SExpression.from_value(v).content(), '42')
        #v = lisp.VNil()
        #self.assertEqual(lisp.SExpression.from_value(v).is_atom(), True)
        #self.assertEqual(lisp.SExpression.from_value(v).content(), 'NIL')
        v = lisp.VSymbol('Alice')
        self.assertEqual(lisp.SExpression.from_value(v).is_atom(), True)
        self.assertEqual(lisp.SExpression.from_value(v).content(), 'alice')
        v = lisp.VSymbol('TEST\u00c9')
        self.assertEqual(lisp.SExpression.from_value(v).is_atom(), True)
        self.assertEqual(lisp.SExpression.from_value(v).content(), 'test\u00e9')
        v = lisp.VEmpty()
        self.assertEqual(lisp.SExpression.from_value(v).is_empty(), True)
        v = lisp.VCons(lisp.VInteger(42), lisp.VEmpty())
        self.assertEqual(lisp.SExpression.from_value(v).is_cons(), True)
        self.assertEqual(lisp.SExpression.from_value(v).content()[0].is_atom(), True)
        self.assertEqual(lisp.SExpression.from_value(v).content()[0].content(), '42')
        self.assertEqual(lisp.SExpression.from_value(v).content()[1].is_empty(), True)
    
        # function? primitive? -- these might be unreadable!?
    


#
# Expressions
#


class TestExp(TestCase):

    def test_symbol(self):
        env = lisp.Environment(bindings=[('Alice', lisp.VInteger(42))])
        e = lisp.Symbol('Alice')
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        e = lisp.Symbol('alice')
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_string(self):
        env = lisp.Environment()
        e = lisp.String('')
        v = e.eval(env)
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '')
        e = lisp.String('Alice')
        v = e.eval(env)
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        # accents
        e = lisp.String('Test\u00e9')
        v = e.eval(env)
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Test\u00e9')


    def test_integer(self):
        env = lisp.Environment()
        e = lisp.Integer(0)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 0)
        e = lisp.Integer(42)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_boolean(self):
        env = lisp.Environment()
        e = lisp.Boolean(True)
        v = e.eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        e = lisp.Boolean(False)
        v = e.eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_if(self):
        # then branch
        env = lisp.Environment([('a', lisp.VInteger(42))])
        e = lisp.If(lisp.Boolean(True), lisp.Symbol('a'), lisp.Symbol('b'))
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # else branch
        e = lisp.If(lisp.Boolean(False), lisp.Symbol('b'), lisp.Symbol('a'))
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_lambda(self):
        # simple
        env = lisp.Environment()
        e = lisp.Lambda(['a', 'b'], lisp.Symbol('a'))
        v = e.eval(env)
        self.assertEqual(v.is_function(), True)
        v = v.apply([lisp.VInteger(42), lisp.VInteger(0)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # environment
        env = lisp.Environment(bindings=[('c', lisp.VInteger(42))])
        e = lisp.Lambda(['a', 'b'], lisp.Symbol('c'))
        v = e.eval(env)
        self.assertEqual(v.is_function(), True)
        v = v.apply([lisp.VInteger(1), lisp.VInteger(0)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_apply(self):
        # simple
        env = lisp.Environment()
        f = lisp.VFunction(['x', 'y'], lisp.Symbol('x'), env)
        env = lisp.Environment(bindings=[('f', f), ('a', lisp.VInteger(42)), ('b', lisp.VInteger(0))])
        e = lisp.Apply(lisp.Symbol('f'),[lisp.Symbol('a'), lisp.Symbol('b')])
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)

        # static vs dynamic binding
        env = lisp.Environment(bindings=[('a', lisp.VInteger(42))])
        f = lisp.VFunction(['x', 'y'], lisp.Symbol('a'), env)
        env = lisp.Environment(bindings=[('f', f), ('a', lisp.VInteger(84)), ('b', lisp.VInteger(0))])
        e = lisp.Apply(lisp.Symbol('f'),[lisp.Symbol('a'), lisp.Symbol('b')])
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_quote(self):
        env = lisp.Environment()
        # symbol
        s = lisp.SAtom('Alice')
        e = lisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'alice')
        # symobl (accents)
        s = lisp.SAtom('TEST\u00c9')
        e = lisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'test\u00e9')
        # string
        s = lisp.SAtom('"Alice"')
        e = lisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        # string (accents)
        s = lisp.SAtom('"Test\u00e9"')
        e = lisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Test\u00e9')
        # integer
        s = lisp.SAtom('42')
        e = lisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # boolean
        s = lisp.SAtom('#t')
        e = lisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        s = lisp.SAtom('#f')
        e = lisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        # empty
        s = lisp.SEmpty()
        e = lisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_empty(), True)
        # cons
        s = lisp.SCons(lisp.SAtom('42'), lisp.SEmpty())
        e = lisp.Quote(s)
        v = e.eval(env)
        self.assertEqual(v.is_cons(), True)
        self.assertEqual(v.car().is_number(), True)
        self.assertEqual(v.car().value(), 42)
        self.assertEqual(v.cdr().is_empty(), True)
        # cons 2
        s = lisp.SCons(lisp.SAtom('42'), lisp.SCons(lisp.SAtom('Alice'), lisp.SEmpty()))
        e = lisp.Quote(s)
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
        env = lisp.Environment(bindings=[('a', lisp.VInteger(42))])
        # empty
        e = lisp.Do([])
        v = e.eval(env)
        self.assertEqual(v.is_nil(), True)
        # single
        e = lisp.Do([lisp.Symbol('a')])
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
        e = lisp.Do([fe1, fe2, lisp.Symbol('a')])
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        self.assertEqual(fe1.value, 42)
        self.assertEqual(fe2.value, 84)


    def test_letrec(self):
        env = lisp.Environment(bindings=[('a', lisp.VInteger(42))])
        # empty
        e = lisp.LetRec([], lisp.Symbol('a'))
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # many / one -> two
        e = lisp.LetRec([('one', lisp.Lambda(['x', 'y'], lisp.Symbol('two'))),
                         ('two', lisp.Lambda(['x'], lisp.Symbol('a')))],
                        lisp.Apply(lisp.Symbol('one'), [lisp.Integer(0), lisp.Integer(0)]))                    
        v = e.eval(env)
        self.assertEqual(v.is_function(), True)
        v = v.apply([lisp.VInteger(0)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # many / two -> one
        e = lisp.LetRec([('one', lisp.Lambda(['x'], lisp.Symbol('a'))),
                         ('two', lisp.Lambda(['x', 'y'], lisp.Symbol('one')))],
                        lisp.Apply(lisp.Symbol('two'), [lisp.Integer(0), lisp.Integer(0)]))                    
        v = e.eval(env)
        self.assertEqual(v.is_function(), True)
        v = v.apply([lisp.VInteger(0)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)

    def test_sexp_to_exp(self):
        env = lisp.Environment(bindings=[('a', lisp.VInteger(42))])
        # symbol
        s = lisp.SAtom('a')
        v = s.to_expression().eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # string
        s = lisp.SAtom('"Alice"')
        v = s.to_expression().eval(env)
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        # integer
        s = lisp.SAtom('42')
        v = s.to_expression().eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # boolean
        s = lisp.SAtom('#t')
        v = s.to_expression().eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        s = lisp.SAtom('#f')
        v = s.to_expression().eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
    

#
# SExpression parsing
#

class TestSExpParsing(TestCase):
    
    def test_sexp_parse_symbol(self):
        inp = 'Alice'
        (s, rest) = lisp.parse_sexp(inp)
        self.assertEqual(rest, '')
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.content(), 'Alice')
        self.assertEqual(s.as_value().is_symbol(), True)
        self.assertEqual(s.as_value().value(), 'alice')
        # accents
        inp = 'TEST\u00c9'
        (s, rest) = lisp.parse_sexp(inp)
        self.assertEqual(s.content(), 'TEST\u00c9')
        self.assertEqual(s.as_value().is_symbol(), True)
        self.assertEqual(s.as_value().value(), 'test\u00e9')


    def test_sexp_parse_string(self):
        inp = '"Alice"'
        (s, rest) = lisp.parse_sexp(inp)
        self.assertEqual(rest, '')
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.content(), '"Alice"')
        self.assertEqual(s.as_value().is_string(), True)
        self.assertEqual(s.as_value().value(), 'Alice')
        # accents
        inp = '"Test\u00e9"'
        (s, rest) = lisp.parse_sexp(inp)
        self.assertEqual(s.content(), '"Test\u00e9"')
        self.assertEqual(s.as_value().is_string(), True)
        self.assertEqual(s.as_value().value(), 'Test\u00e9')


    def test_sexp_parse_integer(self):
        inp = '42'
        (s, rest) = lisp.parse_sexp(inp)
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.content(), '42')
        self.assertEqual(s.as_value().is_number(), True)
        self.assertEqual(s.as_value().value(), 42)


    def test_sexp_parse_boolean(self):
        inp = '#t'
        (s, rest) = lisp.parse_sexp(inp)
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.is_empty(), False)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.content(), '#t')
        self.assertEqual(s.as_value().is_boolean(), True)
        self.assertEqual(s.as_value().value(), True)
        inp = '#f'
        (s, rest) = lisp.parse_sexp(inp)
        self.assertEqual(s.is_atom(), True)
        self.assertEqual(s.content(), '#f')
        self.assertEqual(s.as_value().is_boolean(), True)
        self.assertEqual(s.as_value().value(), False)


    def test_sexp_parse_empty(self):
        inp = '()'
        (s, rest) = lisp.parse_sexp(inp)
        self.assertEqual(s.is_atom(), False)
        self.assertEqual(s.is_empty(), True)
        self.assertEqual(s.is_cons(), False)
        self.assertEqual(s.content(), None)
        self.assertEqual(s.as_value().is_empty(), True)


    def test_sexp_parse_cons(self):
        inp = '(42 Alice Bob)'
        (s, rest) = lisp.parse_sexp(inp)
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
        (s, rest) = lisp.parse_sexp(inp)
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
        (s, rest) = lisp.parse_sexp(inp)
        self.assertEqual(rest, ' xyz')
        inp = 'Alice xyz'
        (s, rest) = lisp.parse_sexp(inp)
        self.assertEqual(rest, ' xyz')
        inp = '"Alice" xyz'
        (s, rest) = lisp.parse_sexp(inp)
        self.assertEqual(rest, ' xyz')
        inp = '#t xyz'
        (s, rest) = lisp.parse_sexp(inp)
        self.assertEqual(rest, ' xyz')
        inp = '#f xyz'
        (s, rest) = lisp.parse_sexp(inp)
        self.assertEqual(rest, ' xyz')
        inp = '() xyz'
        (s, rest) = lisp.parse_sexp(inp)
        self.assertEqual(rest, ' xyz')
        inp = '(Alice Bob) xyz'
        (s, rest) = lisp.parse_sexp(inp)
        self.assertEqual(rest, ' xyz')
    

    
#
# Expression parsing
#


class TestExpParsing(TestCase):

    
    def test_exp_parse_symbol(self):
        env = lisp.Environment(bindings=[('Alice', lisp.VInteger(42))])
        inp = _make_sexp('Alice')
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # accents
        env = lisp.Environment(bindings=[('Test\u00e9', lisp.VInteger(42))])
        inp = _make_sexp('Test\u00e9')
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_exp_parse_string(self):
        env = lisp.Environment()
        inp = _make_sexp('"Alice"')
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        # accents
        inp = _make_sexp('"Test\u00e9"')
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Test\u00e9')


    def test_exp_parse_integer(self):
        env = lisp.Environment()
        inp = _make_sexp('42')
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_exp_parse_boolean(self):
        env = lisp.Environment()
        inp = _make_sexp('#t')
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        inp = _make_sexp('#f')
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_exp_parse_if(self):
        # then branch
        env = lisp.Environment([('a', lisp.VInteger(42))])
        inp = _make_sexp(['if', '#t', 'a', '#f'])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # else branch
        inp = _make_sexp(['if', '#f', '#f', 'a'])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_exp_parse_lambda(self):
        # simple
        env = lisp.Environment()
        inp = _make_sexp(['fn', ['a', 'b'], 'a'])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_function(), True)
        v = v.apply([lisp.VInteger(42), lisp.VInteger(0)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_exp_parse_apply(self):
        env = lisp.Environment()
        f = lisp.VFunction(['x', 'y'], lisp.Symbol('x'), env)
        env = lisp.Environment(bindings=[('f', f), ('a', lisp.VInteger(42)), ('b', lisp.VInteger(0))])
        inp = _make_sexp(['f', 'a', 'b'])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_exp_parse_quote(self):
        env = lisp.Environment()
        # symbol
        inp = _make_sexp(['quote', 'Alice'])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'alice')
        # empty
        inp = _make_sexp(['quote', []])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_empty(), True)
        # cons
        inp = _make_sexp(['quote', ['42']])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_cons(), True)
        self.assertEqual(v.car().is_number(), True)
        self.assertEqual(v.car().value(), 42)
        self.assertEqual(v.cdr().is_empty(), True)


    def test_exp_parse_do(self):
        env = lisp.Environment(bindings=[('a', lisp.VInteger(42))])
        # empty
        inp = _make_sexp(['do'])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_nil(), True)
        # single
        inp = _make_sexp(['do', 'a'])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # many
        inp = _make_sexp(['do', '0', '1', 'a'])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_exp_parse_letrec(self):
        env = lisp.Environment(bindings=[('a', lisp.VInteger(42))])
        # empty
        inp = _make_sexp(['letrec', [], 'a'])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # many
        inp = _make_sexp(['letrec', [['one', ['fn', ['x', 'y'], 'two']],
                                     ['two', ['fn', ['x'], 'a']]],
                          ['one', '0', '0']])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_function(), True)
        v = v.apply([lisp.VInteger(0)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_exp_parse_let(self):
        env = lisp.Environment(bindings=[('a', lisp.VInteger(42))])
        # empty
        inp = _make_sexp(['let', [], 'a'])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # many
        inp = _make_sexp(['let', [['a', '84'], ['b', 'a']], 'a'])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 84)
        inp = _make_sexp(['let', [['a', '84'], ['b', 'a']], 'b'])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_exp_parse_letstar(self):
        env = lisp.Environment(bindings=[('a', lisp.VInteger(42))])
        # empty
        inp = _make_sexp(['let*', [], 'a'])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # many
        inp = _make_sexp(['let*', [['a', '84'], ['b', 'a']], 'a'])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 84)
        inp = _make_sexp(['let*', [['a', '84'], ['b', 'a']], 'b'])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 84)


    def test_exp_parse_and(self):
        env = lisp.Environment(bindings=[('a', lisp.VInteger(42))])
        # empty
        inp = _make_sexp(['and'])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        # many
        inp = _make_sexp(['and', 'a'])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        inp = _make_sexp(['and', '1', 'a' ])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        inp = _make_sexp(['and', '1', '2', 'a' ])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        inp = _make_sexp(['and', '0', '2', 'a' ])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 0)
        inp = _make_sexp(['and', '1', '#f', 'a' ])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_exp_parse_or(self):
        env = lisp.Environment(bindings=[('a', lisp.VInteger(42))])
        # empty
        inp = _make_sexp(['or'])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        # many
        inp = _make_sexp(['or', 'a'])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        inp = _make_sexp(['or', '1', 'a' ])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 1)
        inp = _make_sexp(['or', '0', '2', 'a' ])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 2)
        inp = _make_sexp(['or', '0', '0', 'a' ])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        inp = _make_sexp(['or', '0', '#f', '0' ])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 0)


    def test_exp_parse_loop(self):
        env = lisp.Environment(bindings=[('a', lisp.VInteger(42)),
                                         ('=', lisp.VPrimitive('=', lisp.prim_numequal, 2)),
                                         ('+', lisp.VPrimitive('+', lisp.prim_plus, 2))])
        inp = _make_sexp(['loop', 's', [['n', 'a'], ['sum', '0']],
                          ['if', ['=', 'n', '0'], 'sum',
                           ['s', ['+', 'n', '-1'], ['+', 'sum', 'n']]]])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 903)


    def test_exp_parse_funrec(self):
        env = lisp.Environment(bindings=[('a', lisp.VInteger(42)),
                                         ('=', lisp.VPrimitive('=', lisp.prim_numequal, 2)),
                                         ('+', lisp.VPrimitive('+', lisp.prim_plus, 2))])
        inp = _make_sexp([['funrec', 's', ['n', 'sum'],
                           ['if', ['=', 'n', '0'], 'sum',
                            ['s', ['+', 'n', '-1'], ['+', 'sum', 'n']]]], 'a', '0'])
        e = lisp.Parser().parse_exp(inp)
        v = e.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 903)


#
# Declarations
#

class TestDeclarationParsing(TestCase):

    def test_parse_define(self):
        env = lisp.Environment()
        inp = _make_sexp(['def', 'A', '42'])
        p = lisp.Parser().parse_define(inp)
        self.assertEqual(type(p), type((1, 2)))
        self.assertEqual(p[0], 'a')
        v = p[1].eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)

    def test_parse_defun(self):
        env = lisp.Environment(bindings=[('a', lisp.VInteger(42))])
        inp = _make_sexp(['def', ['FOO', 'A', 'B'], 'a'])
        p = lisp.Parser().parse_defun(inp)
        self.assertEqual(type(p), type((1, 2)))
        self.assertEqual(p[0], 'foo')
        self.assertEqual(p[1], ['a', 'b'])
        v = p[2].eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_parse_decl_define(self):
        env = lisp.Environment()
        inp = _make_sexp(['def', 'A', '42'])
        r = lisp.Parser().parse(inp)
        self.assertEqual(type(r), type((1, 2)))
        self.assertEqual(r[0], 'define')
        p = r[1]
        self.assertEqual(type(p), type((1, 2)))
        self.assertEqual(p[0], 'a')
        v = p[1].eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_parse_decl_defun(self):
        env = lisp.Environment(bindings=[('a', lisp.VInteger(42))])
        inp = _make_sexp(['def', ['FOO', 'A', 'B'], 'a'])
        r = lisp.Parser().parse(inp)
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
        env = lisp.Environment()
        # int
        inp = _make_sexp('42')
        r = lisp.Parser().parse(inp)
        self.assertEqual(type(r), type((1, 2)))
        self.assertEqual(r[0], 'exp')
        p = r[1]
        v = p.eval(env)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # lambda
        inp = _make_sexp(['fn', ['a', 'b'], 'a'])
        r = lisp.Parser().parse(inp)
        self.assertEqual(type(r), type((1, 2)))
        self.assertEqual(r[0], 'exp')
        p = r[1]
        v = p.eval(env)
        self.assertEqual(v.is_function(), True)
        v = v.apply([lisp.VInteger(42), lisp.VInteger(0)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


#
# Operations
#

class TestOperations(TestCase):
    
    def test_prim_type(self):
        v = lisp.prim_type([lisp.VBoolean(True)])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'boolean')
        v = lisp.prim_type([lisp.VString('Alice')])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'string')
        v = lisp.prim_type([lisp.VInteger(42)])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'number')
        v = lisp.prim_type([lisp.VReference(lisp.VInteger(42))])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'ref')
        v = lisp.prim_type([lisp.VNil()])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'nil')
        v = lisp.prim_type([lisp.VEmpty()])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'empty-list')
        v = lisp.prim_type([lisp.VCons(lisp.VInteger(42), lisp.VEmpty())])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'cons-list')
        def prim (args):
            return (args[0], args[1])
        v = lisp.prim_type([lisp.VPrimitive('prim', prim, 2)])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'primitive')
        v = lisp.prim_type([lisp.VSymbol('Alice')])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'symbol')
        v = lisp.prim_type([lisp.VFunction(['a', 'b'], lisp.Symbol('a'), lisp.Environment())])
        self.assertEqual(v.is_symbol(), True)
        self.assertEqual(v.value(), 'function')


    def test_prim_plus(self):
        v = lisp.prim_plus([])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 0)
        v = lisp.prim_plus([lisp.VInteger(42)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        v = lisp.prim_plus([lisp.VInteger(42), lisp.VInteger(84)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42 + 84)
        v = lisp.prim_plus([lisp.VInteger(42), lisp.VInteger(84), lisp.VInteger(168)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42 + 84 + 168)


    def test_prim_times(self):
        v = lisp.prim_times([])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 1)
        v = lisp.prim_times([lisp.VInteger(42)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        v = lisp.prim_times([lisp.VInteger(42), lisp.VInteger(84)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42 * 84)
        v = lisp.prim_times([lisp.VInteger(42), lisp.VInteger(84), lisp.VInteger(168)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42 * 84 * 168)


    def test_prim_minus(self):
        v = lisp.prim_minus([lisp.VInteger(42)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), -42)
        v = lisp.prim_minus([lisp.VInteger(42), lisp.VInteger(84)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42 - 84)
        v = lisp.prim_minus([lisp.VInteger(42), lisp.VInteger(84), lisp.VInteger(168)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42 - 84 - 168)


    def test_prim_numequal(self):
        v = lisp.prim_numequal([lisp.VInteger(0), lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_numequal([lisp.VInteger(42), lisp.VInteger(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_numequal([lisp.VInteger(0), lisp.VInteger(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_numequal([lisp.VInteger(42), lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)


    def test_prim_numless(self):
        v = lisp.prim_numless([lisp.VInteger(0), lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_numless([lisp.VInteger(42), lisp.VInteger(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_numless([lisp.VInteger(0), lisp.VInteger(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_numless([lisp.VInteger(42), lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_numlesseq(self):
        v = lisp.prim_numlesseq([lisp.VInteger(0), lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_numlesseq([lisp.VInteger(42), lisp.VInteger(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_numlesseq([lisp.VInteger(0), lisp.VInteger(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_numlesseq([lisp.VInteger(42), lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)


    def test_prim_numgreater(self):
        v = lisp.prim_numgreater([lisp.VInteger(0), lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_numgreater([lisp.VInteger(42), lisp.VInteger(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_numgreater([lisp.VInteger(0), lisp.VInteger(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_numgreater([lisp.VInteger(42), lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_numgreatereq(self):
        v = lisp.prim_numgreatereq([lisp.VInteger(0), lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_numgreatereq([lisp.VInteger(42), lisp.VInteger(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_numgreatereq([lisp.VInteger(0), lisp.VInteger(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_numgreatereq([lisp.VInteger(42), lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)


    def test_prim_not(self):
        v = lisp.prim_not([lisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_not([lisp.VBoolean(False)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_not([lisp.VInteger(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_not([lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_not([lisp.VString('')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_not([lisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_not([lisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_not([lisp.VCons(lisp.VInteger(42), lisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_string_append(self):
        v = lisp.prim_string_append([])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '')
        v = lisp.prim_string_append([lisp.VString('Alice')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        v = lisp.prim_string_append([lisp.VString('Alice'), lisp.VString('Bob')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'AliceBob')
        v = lisp.prim_string_append([lisp.VString('Alice'), lisp.VString('Bob'), lisp.VString('Charlie')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'AliceBobCharlie')


    def test_prim_string_length(self):
        v = lisp.prim_string_length([lisp.VString('')])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 0)
        v = lisp.prim_string_length([lisp.VString('Alice')])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 5)
        v = lisp.prim_string_length([lisp.VString('Alice Bob')])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 9)


    def test_prim_string_lower(self):
        v = lisp.prim_string_lower([lisp.VString('')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '')
        v = lisp.prim_string_lower([lisp.VString('Alice')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'alice')
        v = lisp.prim_string_lower([lisp.VString('Alice Bob')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'alice bob')


    def test_prim_string_upper(self):
        v = lisp.prim_string_upper([lisp.VString('')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '')
        v = lisp.prim_string_upper([lisp.VString('Alice')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'ALICE')
        v = lisp.prim_string_upper([lisp.VString('Alice Bob')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'ALICE BOB')


    def test_prim_string_substring(self):
        v = lisp.prim_string_substring([lisp.VString('')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '')
        v = lisp.prim_string_substring([lisp.VString('Alice')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        v = lisp.prim_string_substring([lisp.VString('Alice'), lisp.VInteger(0)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        v = lisp.prim_string_substring([lisp.VString('Alice'), lisp.VInteger(1)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'lice')
        v = lisp.prim_string_substring([lisp.VString('Alice'), lisp.VInteger(2)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'ice')
        v = lisp.prim_string_substring([lisp.VString('Alice'), lisp.VInteger(0), lisp.VInteger(5)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        v = lisp.prim_string_substring([lisp.VString('Alice'), lisp.VInteger(0), lisp.VInteger(3)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Ali')
        v = lisp.prim_string_substring([lisp.VString('Alice'), lisp.VInteger(2), lisp.VInteger(3)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'i')
        v = lisp.prim_string_substring([lisp.VString('Alice'), lisp.VInteger(0), lisp.VInteger(0)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '')
        v = lisp.prim_string_substring([lisp.VString('Alice'), lisp.VInteger(3), lisp.VInteger(3)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '')


    def test_prim_apply(self):
        def prim (args):
            return (args[0], args[1])
        v = lisp.prim_apply([lisp.VPrimitive('test', prim, 2, 2),
                             _make_list([lisp.VInteger(42), lisp.VString('Alice')])])
        self.assertEqual(v[0].is_number(), True)
        self.assertEqual(v[0].value(), 42)
        self.assertEqual(v[1].is_string(), True)
        self.assertEqual(v[1].value(), 'Alice')
        v = lisp.prim_apply([lisp.VFunction(['a', 'b'], lisp.Symbol('a'), lisp.Environment()),
                             _make_list([lisp.VInteger(42), lisp.VString('Alice')])])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_prim_cons(self):
        v = lisp.prim_cons([lisp.VInteger(42), lisp.VEmpty()])
        l = _unmake_list(v)
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 42)
        v = lisp.prim_cons([lisp.VInteger(42), _make_list([lisp.VString('Alice'), lisp.VString('Bob')])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 3)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 42)
        self.assertEqual(l[1].is_string(), True)
        self.assertEqual(l[1].value(), 'Alice')
        self.assertEqual(l[2].is_string(), True)
        self.assertEqual(l[2].value(), 'Bob')


    def test_prim_append(self):
        v = lisp.prim_append([])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = lisp.prim_append([_make_list([lisp.VInteger(1), lisp.VInteger(2)])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 2)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 1)
        self.assertEqual(l[1].is_number(), True)
        self.assertEqual(l[1].value(), 2)
        v = lisp.prim_append([_make_list([lisp.VInteger(1), lisp.VInteger(2)]),
                              _make_list([lisp.VInteger(3), lisp.VInteger(4)])])
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
        v = lisp.prim_append([_make_list([lisp.VInteger(1), lisp.VInteger(2)]),
                              _make_list([lisp.VInteger(3), lisp.VInteger(4)]),
                              _make_list([lisp.VInteger(5), lisp.VInteger(6)])])
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
        v = lisp.prim_reverse([_make_list([lisp.VInteger(1),
                                           lisp.VInteger(2),
                                           lisp.VInteger(3),
                                           lisp.VInteger(4)])])
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
        v = lisp.prim_first([_make_list([lisp.VInteger(42)])])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        v = lisp.prim_first([_make_list([lisp.VInteger(42),
                                         lisp.VString('Alice'),
                                         lisp.VString('Bob')])])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_prim_rest(self):
        v = lisp.prim_rest([_make_list([lisp.VInteger(42)])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = lisp.prim_rest([_make_list([lisp.VInteger(42),
                                        lisp.VString('Alice'),
                                        lisp.VString('Bob')])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 2)
        self.assertEqual(l[0].is_string(), True)
        self.assertEqual(l[0].value(), 'Alice')
        self.assertEqual(l[1].is_string(), True)
        self.assertEqual(l[1].value(), 'Bob')


    def test_prim_list(self):
        v = lisp.prim_list([])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = lisp.prim_list([lisp.VInteger(42)])
        l = _unmake_list(v)
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 42)
        v = lisp.prim_list([lisp.VInteger(42),
                            lisp.VString('Alice')])
        l = _unmake_list(v)
        self.assertEqual(len(l), 2)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 42)
        self.assertEqual(l[1].is_string(), True)
        self.assertEqual(l[1].value(), 'Alice')
        v = lisp.prim_list([lisp.VInteger(42),
                            lisp.VString('Alice'),
                            lisp.VString('Bob')])
        l = _unmake_list(v)
        self.assertEqual(len(l), 3)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 42)
        self.assertEqual(l[1].is_string(), True)
        self.assertEqual(l[1].value(), 'Alice')
        self.assertEqual(l[2].is_string(), True)
        self.assertEqual(l[2].value(), 'Bob')


    def test_prim_length(self):
        v = lisp.prim_length([_make_list([])])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 0)
        v = lisp.prim_length([_make_list([lisp.VInteger(42)])])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 1)
        v = lisp.prim_length([_make_list([lisp.VInteger(42),
                                          lisp.VString('Alice')])])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 2)
        v = lisp.prim_length([_make_list([lisp.VInteger(42),
                                          lisp.VString('Alice'),
                                          lisp.VString('Bob')])])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 3)


    def test_prim_nth(self):
        v = lisp.prim_nth([_make_list([lisp.VInteger(42),
                                       lisp.VString('Alice'),
                                       lisp.VString('Bob')]),
                           lisp.VInteger(0)])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        v = lisp.prim_nth([_make_list([lisp.VInteger(42),
                                       lisp.VString('Alice'),
                                       lisp.VString('Bob')]),
                           lisp.VInteger(1)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')
        v = lisp.prim_nth([_make_list([lisp.VInteger(42),
                                       lisp.VString('Alice'),
                                       lisp.VString('Bob')]),
                           lisp.VInteger(2)])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Bob')


    def test_prim_map(self):
        def prim1 (args):
            return args[0]
        def prim2 (args):
            return args[1]
        v = lisp.prim_map([lisp.VPrimitive('test', prim1, 1),
                           _make_list([])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = lisp.prim_map([lisp.VPrimitive('test', prim1, 1),
                           _make_list([lisp.VInteger(42),
                                       lisp.VString('Alice'),
                                       lisp.VString('Bob')])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 3)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 42)
        self.assertEqual(l[1].is_string(), True)
        self.assertEqual(l[1].value(), 'Alice')
        self.assertEqual(l[2].is_string(), True)
        self.assertEqual(l[2].value(), 'Bob')
        v = lisp.prim_map([lisp.VPrimitive('test', prim2, 2),
                           _make_list([]),
                           _make_list([])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = lisp.prim_map([lisp.VPrimitive('test', prim2, 2),
                           _make_list([]),
                           _make_list([lisp.VInteger(42)])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = lisp.prim_map([lisp.VPrimitive('test', prim2, 2),
                           _make_list([lisp.VInteger(42),
                                       lisp.VString('Alice'),
                                       lisp.VString('Bob')]),
                           _make_list([lisp.VInteger(84),
                                       lisp.VString('Charlie'),
                                       lisp.VString('Darlene')])])
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
            return lisp.VBoolean(False)
        def prim_int (args):
            return lisp.VBoolean(args[0].is_number())
        v = lisp.prim_filter([lisp.VPrimitive('test', prim_none, 1),
                              _make_list([])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = lisp.prim_filter([lisp.VPrimitive('test', prim_none, 1),
                              _make_list([lisp.VInteger(42),
                                          lisp.VString('Alice'),
                                          lisp.VString('Bob')])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 0)
        v = lisp.prim_filter([lisp.VPrimitive('test', prim_int, 1),
                              _make_list([lisp.VInteger(42),
                                          lisp.VString('Alice'),
                                          lisp.VString('Bob')])])
        l = _unmake_list(v)
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].is_number(), True)
        self.assertEqual(l[0].value(), 42)


    def test_prim_foldr(self):
        def prim (args):
            return lisp.VString(args[0].value() + '(' + args[1].value() + ')')
        v = lisp.prim_foldr([lisp.VPrimitive('test', prim, 2),
                             _make_list([]),
                             lisp.VString('base')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'base')
        v = lisp.prim_foldr([lisp.VPrimitive('test', prim, 2),
                             _make_list([lisp.VString('Alice'),
                                         lisp.VString('Bob'),
                                         lisp.VString('Charlie')]),
                             lisp.VString('base')])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice(Bob(Charlie(base)))')


    def test_prim_foldl(self):
        def prim (args):
            return lisp.VString('(' + args[0].value() + ')' + args[1].value())
        v = lisp.prim_foldl([lisp.VPrimitive('test', prim, 2),
                             lisp.VString('base'),
                             _make_list([])])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'base')
        v = lisp.prim_foldl([lisp.VPrimitive('test', prim, 2),
                             lisp.VString('base'),
                             _make_list([lisp.VString('Alice'),
                                         lisp.VString('Bob'),
                                         lisp.VString('Charlie')])])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), '(((base)Alice)Bob)Charlie')


    def test_prim_eqp(self):
        v = lisp.prim_eqp([lisp.VInteger(42),
                           lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_eqp([lisp.VInteger(42),
                           lisp.VInteger(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        lst = _make_list([lisp.VInteger(42)])
        v = lisp.prim_eqp([lst, lst])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_eqp([lst, _make_list([lisp.VInteger(42)])])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_eqp([lst, lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_eqp([lst, _make_list([lisp.VInteger(84)])])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_eqlp(self):
        v = lisp.prim_eqlp([lisp.VInteger(42),
                           lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_eqlp([lisp.VInteger(42),
                           lisp.VInteger(0)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        lst = _make_list([lisp.VInteger(42)])
        v = lisp.prim_eqlp([lst, lst])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_eqlp([lst, _make_list([lisp.VInteger(42)])])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_eqlp([lst, lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_eqlp([lst, _make_list([lisp.VInteger(84)])])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        ref = lisp.VReference(lisp.VInteger(42))
        v = lisp.prim_eqlp([ref, ref])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_eqlp([ref, lisp.VReference(lisp.VInteger(42))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_eqlp([ref, lisp.VReference(lisp.VInteger(0))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_emptyp(self):
        v = lisp.prim_emptyp([lisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_emptyp([lisp.VCons(lisp.VInteger(42), lisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_emptyp([lisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_emptyp([lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_emptyp([lisp.VReference(lisp.VInteger(42))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_emptyp([lisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_emptyp([lisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_emptyp([lisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_emptyp([lisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_emptyp([lisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = lisp.prim_emptyp([lisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_emptyp([lisp.VFunction(['a'], lisp.VSymbol('a'), lisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_consp(self):
        v = lisp.prim_consp([lisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_consp([lisp.VCons(lisp.VInteger(42), lisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_consp([lisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_consp([lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_consp([lisp.VReference(lisp.VInteger(42))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_consp([lisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_consp([lisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_consp([lisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_consp([lisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_consp([lisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = lisp.prim_consp([lisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_consp([lisp.VFunction(['a'], lisp.VSymbol('a'), lisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_listp(self):
        v = lisp.prim_listp([lisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_listp([lisp.VCons(lisp.VInteger(42), lisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_listp([lisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_listp([lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_listp([lisp.VReference(lisp.VInteger(42))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_listp([lisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_listp([lisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_listp([lisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_listp([lisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_listp([lisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = lisp.prim_listp([lisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_listp([lisp.VFunction(['a'], lisp.VSymbol('a'), lisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_numberp(self):
        v = lisp.prim_numberp([lisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_numberp([lisp.VCons(lisp.VInteger(42), lisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_numberp([lisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_numberp([lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_numberp([lisp.VReference(lisp.VInteger(42))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_numberp([lisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_numberp([lisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_numberp([lisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_numberp([lisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_numberp([lisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = lisp.prim_numberp([lisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_numberp([lisp.VFunction(['a'], lisp.VSymbol('a'), lisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_booleanp(self):
        v = lisp.prim_booleanp([lisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_booleanp([lisp.VCons(lisp.VInteger(42), lisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_booleanp([lisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_booleanp([lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_booleanp([lisp.VReference(lisp.VInteger(42))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_booleanp([lisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_booleanp([lisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_booleanp([lisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_booleanp([lisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_booleanp([lisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = lisp.prim_booleanp([lisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_booleanp([lisp.VFunction(['a'], lisp.VSymbol('a'), lisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_stringp(self):
        v = lisp.prim_stringp([lisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_stringp([lisp.VCons(lisp.VInteger(42), lisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_stringp([lisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_stringp([lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_stringp([lisp.VReference(lisp.VInteger(42))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_stringp([lisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_stringp([lisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_stringp([lisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_stringp([lisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_stringp([lisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = lisp.prim_stringp([lisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_stringp([lisp.VFunction(['a'], lisp.VSymbol('a'), lisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_symbolp(self):
        v = lisp.prim_symbolp([lisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_symbolp([lisp.VCons(lisp.VInteger(42), lisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_symbolp([lisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_symbolp([lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_symbolp([lisp.VReference(lisp.VInteger(42))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_symbolp([lisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_symbolp([lisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_symbolp([lisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_symbolp([lisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_symbolp([lisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = lisp.prim_symbolp([lisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_symbolp([lisp.VFunction(['a'], lisp.VSymbol('a'), lisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_functionp(self):
        v = lisp.prim_functionp([lisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_functionp([lisp.VCons(lisp.VInteger(42), lisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_functionp([lisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_functionp([lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_functionp([lisp.VReference(lisp.VInteger(42))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_functionp([lisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_functionp([lisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_functionp([lisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_functionp([lisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_functionp([lisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False )
        v = lisp.prim_functionp([lisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_functionp([lisp.VFunction(['a'], lisp.VSymbol('a'), lisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)


    def test_prim_nilp(self):
        v = lisp.prim_nilp([lisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_nilp([lisp.VCons(lisp.VInteger(42), lisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_nilp([lisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_nilp([lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_nilp([lisp.VReference(lisp.VInteger(42))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_nilp([lisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_nilp([lisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_nilp([lisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_nilp([lisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_nilp([lisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True )
        v = lisp.prim_nilp([lisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_nilp([lisp.VFunction(['a'], lisp.VSymbol('a'), lisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_refp(self):
        v = lisp.prim_refp([lisp.VEmpty()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_refp([lisp.VCons(lisp.VInteger(42), lisp.VEmpty())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_refp([lisp.VBoolean(True)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_refp([lisp.VInteger(42)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_refp([lisp.VReference(lisp.VInteger(42))])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), True)
        v = lisp.prim_refp([lisp.VString('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_refp([lisp.VString('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_refp([lisp.VSymbol('Alice')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_refp([lisp.VSymbol('Test\u00e9')])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_refp([lisp.VNil()])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_refp([lisp.VPrimitive('test', lambda args: args[0], 1)])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)
        v = lisp.prim_refp([lisp.VFunction(['a'], lisp.VSymbol('a'), lisp.Environment())])
        self.assertEqual(v.is_boolean(), True)
        self.assertEqual(v.value(), False)


    def test_prim_ref(self):
        val = lisp.VInteger(42)
        v = lisp.prim_ref([val])
        self.assertEqual(v.is_reference(), True)
        self.assertEqual(v.value(), val)
        val = lisp.VString("Alice")
        v = lisp.prim_ref([val])
        self.assertEqual(v.is_reference(), True)
        self.assertEqual(v.value(), val)
        val = lisp.VReference(lisp.VInteger(42))
        v = lisp.prim_ref([val])
        self.assertEqual(v.is_reference(), True)
        self.assertEqual(v.value(), val)


    def test_prim_ref_get(self):
        val = lisp.VReference(lisp.VInteger(42))
        v = lisp.prim_ref_get([val])
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        val = lisp.VReference(lisp.VString("Alice"))
        v = lisp.prim_ref_get([val])
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), "Alice")
        val = lisp.VReference(lisp.VReference(lisp.VInteger(42)))
        v = lisp.prim_ref_get([val])
        self.assertEqual(v.is_reference(), True)
        self.assertEqual(v.value().is_number(), True)
        self.assertEqual(v.value().value(), 42)


    def test_prim_ref_set(self):
        val = lisp.VReference(lisp.VInteger(0))
        v = lisp.prim_ref_set([val, lisp.VInteger(42)])
        self.assertEqual(v.is_nil(), True)
        self.assertEqual(val.value().is_number(), True)
        self.assertEqual(val.value().value(), 42)
        val = lisp.VReference(lisp.VInteger(0))
        v = lisp.prim_ref_set([val, lisp.VString("Alice")])
        self.assertEqual(v.is_nil(), True)
        self.assertEqual(val.value().is_string(), True)
        self.assertEqual(val.value().value(), "Alice")
        val = lisp.VReference(lisp.VInteger(0))
        v = lisp.prim_ref_set([val, lisp.VReference(lisp.VInteger(42))])
        self.assertEqual(v.is_nil(), True)
        self.assertEqual(val.value().is_reference(), True)
        self.assertEqual(val.value().value().is_number(), True)
        self.assertEqual(val.value().value().value(), 42)
    
#
# Engine
#

class TestEngine(TestCase):
    
    def test_engine_read(self):
        engine = lisp.Engine()
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
        engine = lisp.Engine()
        inp = _make_sexp('42')
        v = engine.eval_sexp(inp)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # application
        engine = lisp.Engine()
        inp = _make_sexp([['fn', ['a', 'b'], 'a'], '42', '0'])
        v = engine.eval_sexp(inp)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # define
        engine = lisp.Engine()
        inp = _make_sexp(['def', 'a', '42'])
        engine.eval_sexp(inp)
        v = engine.eval_sexp(_make_sexp('a'))
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # defun
        engine = lisp.Engine()
        inp = _make_sexp(['def', ['foo', 'a'], 'a'])
        engine.eval_sexp(inp)
        v = engine.eval_sexp(_make_sexp(['foo', '42']))
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_engine_eval(self):
        # integer
        engine = lisp.Engine()
        inp = '42'
        v = engine.eval(inp)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # application
        engine = lisp.Engine()
        inp = '((fn (a b) a) 42 0)'
        v = engine.eval(inp)
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # define
        engine = lisp.Engine()
        inp = '(def a 42)'
        engine.eval(inp)
        v = engine.eval('a')
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        # defun
        engine = lisp.Engine()
        inp = '(def (foo a) a)'
        engine.eval(inp)
        v = engine.eval('(foo 42)')
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)


    def test_engine_bindings(self):
        # no init bindings
        engine = lisp.Engine()
        v = engine.eval('type')
        self.assertEqual(v.is_function(), True)
        v = engine.eval('empty')
        self.assertEqual(v.is_empty(), True)
        # init bindings
        engine = lisp.Engine(bindings=[('a', lisp.VInteger(42)), ('b', lisp.VString('Alice'))])
        v = engine.eval('a')
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        v = engine.eval('b')
        self.assertEqual(v.is_string(), True)
        self.assertEqual(v.value(), 'Alice')


    def test_engine_add_env(self):
        # no init bindings
        engine = lisp.Engine()
        engine.add_env([('a', lisp.VInteger(42)), ('b', lisp.VString('Alice'))])
        v = engine.eval('a')
        self.assertEqual(v.is_number(), True)
        self.assertEqual(v.value(), 42)
        v = engine.eval('empty')
        self.assertEqual(v.is_empty(), True)
        # init bindings
        engine = lisp.Engine(bindings=[('x', lisp.VInteger(42)), ('y', lisp.VString('Alice'))])
        engine.add_env([('a', lisp.VInteger(42)), ('b', lisp.VString('Alice'))])
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
        engine = lisp.Engine()
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
    
    
