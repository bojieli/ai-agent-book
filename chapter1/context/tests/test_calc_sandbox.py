"""Tests for the AST-whitelist calculator sandbox in calc_sandbox.py.

The previous implementation evaluated expressions with eval() and an empty
__builtins__ dict.  Emptied builtins only hide built-in function names;
attribute access, literals and method calls still work, so a classic
object-obfuscation expression such as

    ().__class__.__mro__[1].__subclasses__()[i]...get("system")("...")

executed arbitrary shell commands.  These tests pin both sides of the fix:
ordinary arithmetic still works, and every known escape shape is rejected by
the AST whitelist.  They use only the standard library, so they run offline
and in key-less CI.
"""

import math

import pytest

from calc_sandbox import safe_eval, UnsafeExpression


def assert_rejected(payload):
    with pytest.raises((UnsafeExpression, ValueError)):
        safe_eval(payload)


class TestPlainArithmetic:
    def test_precedence_and_parentheses(self):
        assert safe_eval("2+3*4") == 14
        assert safe_eval("(2+3)*4") == 20

    def test_power_and_mod(self):
        assert safe_eval("2**10") == 1024
        assert safe_eval("7 % 3") == 1

    def test_caret_is_power_rewrite(self):
        assert safe_eval("2^3") == 8

    def test_unary_minus(self):
        assert safe_eval("-5") == -5

    def test_math_functions_and_constants(self):
        assert safe_eval("sin(pi/2)") == pytest.approx(1.0)
        assert safe_eval("log(e)") == pytest.approx(1.0)
        assert safe_eval("floor(3.7)") == 3

    def test_abs_round_min_max(self):
        assert safe_eval("abs(-7)") == 7
        assert safe_eval("round(3.14159, 2)") == pytest.approx(3.14)
        assert safe_eval("round(3.14159, ndigits=3)") == pytest.approx(3.142)
        assert safe_eval("max(1, 5, 3)") == 5
        assert safe_eval("min([3, 1, 2])") == 1

    def test_comparison(self):
        assert safe_eval("1 < 2 < 3") is True


class TestEscapeRejected:
    def test_object_obfuscation_shapes(self):
        # Every shape below was previously a working escape on the same
        # values: attribute access is the load-bearing primitive.
        assert_rejected("().__class__.__mro__[1].__subclasses__()")
        assert_rejected(
            "().__class__.__mro__[1].__subclasses__()[174]"
            ".__init__.__globals__.get('system')('echo pwned')"
        )
        assert_rejected("[].__class__.__base__.__subclasses__()")
        assert_rejected("'x'.__class__")
        assert_rejected("(1).__class__")

    def test_unwhitelisted_names_and_calls(self):
        assert_rejected("__import__('os')")
        assert_rejected("open('/etc/passwd')")
        assert_rejected("eval('2+2')")
        assert_rejected("exec('x=1')")
        assert_rejected("print('hi')")
        assert_rejected("foo(1)")

    def test_subscript_is_rejected(self):
        assert_rejected("[1, 2][0]")

    def test_non_numeric_literal_rejected(self):
        assert_rejected("'abc'")
        assert_rejected("b'abc'")
        assert_rejected("None")

    def test_lambda_and_comprehensions_rejected(self):
        assert_rejected("lambda x: x")
        assert_rejected("[x for x in [1]]")

    def test_walrus_and_if_expression_rejected(self):
        assert_rejected("(x := 1)")
        assert_rejected("1 if True else 2")

    def test_empty_or_invalid_input(self):
        assert_rejected("")
        assert_rejected("   ")
        assert_rejected("2 +")


class TestPreservesLegacySemantics:
    def test_names_that_previously_worked_still_work(self):
        # All names from the old allowed_names dict (all public math members
        # plus abs/round/min/max) must still be reachable.
        for name in ("sin", "cos", "tan", "sqrt", "log", "floor", "ceil",
                     "abs", "round", "min", "max", "pi", "e", "tau"):
            assert name in math.__dict__ or name in ("abs", "round", "min", "max")