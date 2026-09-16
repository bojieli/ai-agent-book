"""Safe mathematical expression evaluation via an AST whitelist.

Background
----------
The calculator previously evaluated expressions with

    eval(expression, {"__builtins__": {}}, allowed_names)

Emptying __builtins__ only removes the built-in *function names*. Attribute
access, literals and method calls never go through __builtins__, so the
classic object-obfuscation escape works unchanged:

    ().__class__.__mro__[1].__subclasses__()[i]...get("system")("echo pwned")

The only way to make such an expression inert is to validate the *syntax tree*
and reject the node types (attribute access, subscripting, calls of anything
not on an explicit whitelist) before the interpreter ever sees them.  This
module does exactly that.  The name whitelist keeps every public attribute of
math plus abs / round / min / max, mirroring the previous allowed_names dict,
so the arithmetic surface the calculator supported is preserved.
"""

import ast
import math

# Names the calculator may reference: every public attribute of `math`
# (functions such as sin/floor, constants such as pi/e) plus a handful of
# Python builtins, mirroring the old allowed_names dict.
ALLOWED_NAMES = {
    name: getattr(math, name) for name in dir(math) if not name.startswith("_")
}
ALLOWED_NAMES.update({"abs": abs, "round": round, "min": min, "max": max})

_DECIMAL_OPS = (
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow)
_UNARY_OPS = (ast.USub, ast.UAdd)
_COMPARE_OPS = (ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq)


class UnsafeExpression(ValueError):
    """Raised when the expression uses syntax outside the calculator whitelist."""


def _check_op(node, allowed):
    if not isinstance(node, allowed):
        raise UnsafeExpression(f"unsupported operator: {type(node).__name__}")


def _check(node):
    """Recursively validate that every node is on the whitelist."""
    if isinstance(node, ast.Expression):
        _check(node.body)
    elif isinstance(node, ast.BinOp):
        _check(node.left)
        _check(node.right)
        _check_op(node.op, _DECIMAL_OPS)
    elif isinstance(node, ast.UnaryOp):
        _check(node.operand)
        _check_op(node.op, _UNARY_OPS)
    elif isinstance(node, ast.Compare):
        _check(node.left)
        for comparator in node.comparators:
            _check(comparator)
        for op in node.ops:
            _check_op(op, _COMPARE_OPS)
    elif isinstance(node, ast.Call):
        # Only whitelisted names may be called; anything else (method calls,
        # attribute access, ...) aborts before reaching the interpreter.
        if not isinstance(node.func, ast.Name) or node.func.id not in ALLOWED_NAMES:
            raise UnsafeExpression("only whitelisted functions may be called")
        for arg in node.args:
            _check(arg)
        for keyword in node.keywords:
            if keyword.arg is None:
                raise UnsafeExpression("**kwargs is not allowed")
            _check(keyword.value)
    elif isinstance(node, ast.Name):
        if node.id not in ALLOWED_NAMES:
            raise UnsafeExpression(f"unknown name: {node.id!r}")
    elif isinstance(node, ast.Constant):
        # Numeric literals only: strings/bytes are an attack surface.
        if not isinstance(node.value, (int, float, complex, bool)):
            raise UnsafeExpression("only numeric literals are allowed")
    elif isinstance(node, (ast.List, ast.Tuple)):
        for elt in node.elts:
            _check(elt)
    else:
        # Everything else -- Attribute, Subscript, comprehensions, lambdas,
        # f-strings ... -- is refused.
        raise UnsafeExpression(f"unsupported syntax: {type(node).__name__}")


def safe_eval(expression):
    """Evaluate a whitelisted mathematical expression and return its value.

    Raises:
        UnsafeExpression: if the expression uses syntax outside the whitelist.
        ValueError: for empty input or unparsable expressions.
    """
    if not isinstance(expression, str) or not expression.strip():
        raise ValueError("empty expression")
    # Keep the caret-to-power rewrite the original calculator applied, so
    # existing prompts keep working.
    expression = expression.replace("^", "**")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"invalid expression: {exc}") from exc
    _check(tree)
    return eval(compile(tree, "<safe_calc>", "eval"), {"__builtins__": {}}, ALLOWED_NAMES)