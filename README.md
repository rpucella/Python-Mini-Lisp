# Python Mini Lisp

This repo is a simple one-file LISP interpreter ready for embedding in a Python program to provide an internal command language.

It has no external dependencies outside the Python 3.8 standard library. It should work on earlier versions than 3.8, but I haven't tested it.

The focus of the code is on clarity and not efficiency. Running an interpreted language on top of a Python interpreter will never win any prize for speed in the best of all worlds. The structure of the interpreter is entirely straightforward: there is a class `Value` to represent run-time values, a class `Expression` to represent the abstract syntax trees, a class `Reader` to transform a string into an s-expression (represented as an instance of `Value`), and a class `Parser` to parse an s-expression into an AST. A class `Environment` provides environment for binding names to values. Class `Expression` has a method `eval()` that evaluates the expression to a value. 

The only moderately subtle bit of coding is the use of a method `evalPartial()` in class `Expression` to handle evaluating expressions with [tail-call optimization](https://en.wikipedia.org/wiki/Tail_call): intuitively, if the last thing a function does is evaluate a function call, the evaluation should not create a invocation frame on the stack when evaluating the final function call. That turns out to be tricky to implement using a language like Python that does not support tail-call optimization natively. The trick is to implement evaluation not as a recursive method, but as a loop that invokes `evalPartial()` to partially evaluate an expression until the final expression is reached, and loop with that final expression as the new expression to evaluate. Rinse and repeat until you get a value. (This is basically a form of [trampolining](https://en.wikipedia.org/wiki/Trampoline_(computing)).)

## Usage

Just drop the file `mlisp.py` into your project, and import it.

You can create a interpreter engine by instantiating the class `Engine`:

    eng = Engine()

Once you have an engine `eng`, you can read and evaluate a string `str` using

    eng.eval(eng.read(str))

such as:

    eng.eval(eng.read('(+ 1 2)'))

Method `read()` will turn the string into an s-expression, and method `eval()` will evaluate that s-expression into a value.

**TODO**: Add more details on the API and the underlying language.


## Extending the engine

You can add new primitive operations by calling method `def_primitive()` of the engine - a primitive requires a name, an underlying Python function that takes the name of the primitive (mostly for error reporting) and a list of values (supplied when the operation is called) and returns a value, as well as the minimum number of arguments to the primitive and the maximum number of arguments (None if no limit).

You can add new types to the language by adding a new subclass of `Value`. You only need to provide a `kind()` method that returns a string describing the type. You will want new primitive operations to work with these new types. You may also want a reader macro that can read the external representation of values of such types. You can register reader macros using method `register_reader` of the engine.

You can define new syntactic macros (functions from s-expressions to s-expressions applied during parsing) using method `register_macro` of the engine.


## Testing

You can run the unit tests using

    python -m unittest tests.py

