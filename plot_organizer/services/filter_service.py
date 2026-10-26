"""Row filtering with pandas query-style expressions.

A data filter is a text expression such as ``time >= 0 and Country == "USA"``
that is evaluated against a DataFrame before plotting. Filters are stored in
.ppo project files, which can be shared, so every expression is checked against
an allowlist before pandas evaluates it.
"""
from __future__ import annotations

import ast
import difflib
import re
import warnings
from typing import Any, Literal, Optional

import numpy as np
import pandas as pd

ColumnKind = Literal["numeric", "boolean", "datetime", "text"]

# Attribute names that may appear in an expression, e.g. `name.str.contains("x")`,
# `date.dt.year`, `value.isna()`. Anything else (to_csv, __class__, ...) is rejected.
ALLOWED_ATTRIBUTES = frozenset({
    "str", "dt",
    "contains", "startswith", "endswith", "match", "fullmatch",
    "lower", "upper", "strip", "len",
    "isna", "notna", "isnull", "notnull",
    "between", "isin", "abs", "round",
    "year", "month", "day", "hour", "minute", "dayofweek", "date",
})

# Plain function calls supported by pandas.eval, e.g. `abs(delta) > 1`.
ALLOWED_FUNCTIONS = frozenset({
    "abs", "sqrt", "exp", "log", "log1p", "expm1",
    "sin", "cos", "tan", "sinh", "cosh", "tanh",
    "arcsin", "arccos", "arctan", "arcsinh", "arccosh", "arctanh", "arctan2",
})

_ALLOWED_NODES = (
    ast.Expression, ast.BoolOp, ast.And, ast.Or,
    ast.UnaryOp, ast.Not, ast.Invert, ast.USub, ast.UAdd,
    ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow, ast.FloorDiv,
    ast.BitAnd, ast.BitOr, ast.BitXor,
    ast.Compare, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn,
    ast.Name, ast.Load, ast.Constant, ast.List, ast.Tuple,
    ast.Attribute, ast.Call, ast.keyword,
)

_BACKTICK_RE = re.compile(r"`([^`]*)`")
_PLACEHOLDER = "_qp_col{}_"
_DATE_SEPARATORS = re.compile(r"[-/:]")


class FilterError(ValueError):
    """Raised when a data filter is invalid or cannot be evaluated.

    The message is written for the end user and is shown as-is in the GUI.
    """


def column_kind(series: pd.Series) -> ColumnKind:
    """Classify a column for filtering purposes.

    CSV files are loaded without date parsing, so date columns arrive as text;
    they are reported as "datetime" when most values look like dates.
    """
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    values = series.dropna()
    if values.empty:
        return "text"
    if values.head(1000).map(lambda v: isinstance(v, bool)).all():
        return "boolean"
    if _looks_like_dates(values.head(200).astype(str)):
        return "datetime"
    return "text"


def is_numeric_like(series: pd.Series) -> bool:
    """True for text columns whose values are mostly numbers (e.g. 1, 2, 3, "All")."""
    if pd.api.types.is_numeric_dtype(series):
        return False
    values = series.dropna().head(1000).astype(str)
    if values.empty:
        return False
    return pd.to_numeric(values, errors="coerce").notna().mean() >= 0.5


def _looks_like_dates(sample: pd.Series) -> bool:
    # Plain numbers ("1988") parse as dates too, so require separators and
    # rule out mostly-numeric columns first.
    if pd.to_numeric(sample, errors="coerce").notna().mean() >= 0.9:
        return False
    if sample.str.contains(_DATE_SEPARATORS).mean() < 0.9:
        return False
    parsed = _to_datetime(sample)
    return parsed is not None and parsed.notna().mean() >= 0.9


def _to_datetime(series: pd.Series) -> Optional[pd.Series]:
    """Parse text to datetimes, returning None when the column can't be parsed."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            return pd.to_datetime(series, errors="coerce", format="mixed")
        except (ValueError, TypeError):
            pass
        try:
            # Mixed timezone offsets: normalise everything to UTC
            return pd.to_datetime(series, errors="coerce", format="mixed", utc=True)
        except (ValueError, TypeError):
            return None


def normalize_expression(expr: Optional[str]) -> str:
    """Join a multi-line expression into one line (pandas treats lines as statements)."""
    if not expr:
        return ""
    return expr.replace("\r", " ").replace("\n", " ").strip()


def _parse(expr: str) -> tuple[ast.Expression, dict[str, str]]:
    """Parse an expression, replacing `backticked names` with placeholder identifiers."""
    placeholders: dict[str, str] = {}

    def repl(match: re.Match) -> str:
        name = _PLACEHOLDER.format(len(placeholders))
        placeholders[name] = match.group(1)
        return name

    cleaned = _BACKTICK_RE.sub(repl, expr)
    try:
        tree = ast.parse(cleaned, mode="eval")
    except SyntaxError as e:
        raise FilterError(_syntax_message(expr, e)) from None
    return tree, placeholders


def _syntax_message(expr: str, error: SyntaxError) -> str:
    if "@" in expr:
        return "'@' variable references are not supported in filters."
    if expr.count("`") % 2:
        return "Unmatched backtick (`) in filter."
    msg = "Syntax error in filter"
    if error.offset:
        msg += f" near position {error.offset}"
    return msg + (
        ". Check quotes and parentheses; combine conditions with 'and' / 'or', "
        "and wrap column names containing spaces in backticks, e.g. `Number of employees`."
    )


def validate_expression(expr: str, columns: Optional[list[str]] = None) -> set[str]:
    """Check an expression against the allowlist and return the columns it references.

    Raises FilterError for syntax errors or disallowed constructs (method calls
    outside the allowlist, dunder access, '@' references, lambdas, ...).
    """
    expr = normalize_expression(expr)
    tree, placeholders = _parse(expr)
    known = set(columns) if columns is not None else None
    referenced: set[str] = set()

    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise FilterError(
                f"'{type(node).__name__}' expressions are not allowed in filters."
            )
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.MatMult):
            raise FilterError("'@' variable references are not supported in filters.")
        if isinstance(node, ast.Attribute) and node.attr not in ALLOWED_ATTRIBUTES:
            raise FilterError(f"'.{node.attr}' is not allowed in filters.")
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                if func.id not in ALLOWED_FUNCTIONS:
                    raise FilterError(f"Function '{func.id}()' is not allowed in filters.")
            elif not isinstance(func, ast.Attribute):
                raise FilterError("Only column methods such as .str.contains() can be called.")
            for kw in node.keywords:
                if kw.arg is None or not isinstance(kw.value, ast.Constant):
                    raise FilterError("Keyword arguments must be plain values, e.g. case=False.")
        if isinstance(node, ast.Name):
            if node.id.startswith("__"):
                raise FilterError(f"'{node.id}' is not allowed in filters.")
            name = placeholders.get(node.id, node.id)
            if known is None or name in known:
                referenced.add(name)
    return referenced


def apply_data_filter(df: pd.DataFrame, expr: Optional[str]) -> pd.DataFrame:
    """Return the rows of df matching a query expression.

    A blank expression returns df unchanged. Date-like text columns referenced
    by the expression are compared as datetimes, so `date >= "2024-01-01"`
    works for any date format. The returned rows keep their original dtypes.
    """
    expr = normalize_expression(expr)
    if not expr:
        return df

    columns = [str(c) for c in df.columns]
    try:
        referenced = validate_expression(expr, columns)
    except FilterError:
        _check_unquoted_column_names(expr, columns)
        raise

    eval_df = df
    for col in referenced:
        series = df[col]
        if series.dtype == object and column_kind(series) == "datetime":
            converted = _to_datetime(series)
            if converted is not None:
                if eval_df is df:
                    eval_df = df.copy(deep=False)
                eval_df[col] = converted

    try:
        result = eval_df.eval(
            expr, engine="python", parser="pandas", local_dict={}, global_dict={}
        )
    except FilterError:
        raise
    except pd.errors.UndefinedVariableError as e:
        raise FilterError(_undefined_message(str(e), columns)) from None
    except TypeError as e:
        raise FilterError(_type_mismatch_message(str(e), df, referenced)) from None
    except SyntaxError as e:
        raise FilterError(_syntax_message(expr, e)) from None
    except Exception as e:  # pandas raises a wide variety of errors here
        raise FilterError(f"Could not evaluate filter: {e}") from None

    mask = _to_bool_mask(result)
    return df[mask.to_numpy()]


def apply_filters(
    df: pd.DataFrame,
    data_filter: Optional[str] = None,
    filter_query: Optional[dict[str, Any]] = None,
) -> pd.DataFrame:
    """Apply the user data filter, then the equality filters from group faceting."""
    out = apply_data_filter(df, data_filter)
    if filter_query:
        for col, val in filter_query.items():
            out = out[out[col] == val]
    return out


def filter_warnings(df: pd.DataFrame, expr: Optional[str]) -> list[str]:
    """Best-effort lint for comparisons that silently match nothing.

    Flags comparisons between a column and a literal of the wrong type, e.g. a
    numeric column compared with "22" or a text column compared with 1.
    Never raises; returns an empty list for invalid expressions.
    """
    expr = normalize_expression(expr)
    if not expr:
        return []
    try:
        tree, placeholders = _parse(expr)
    except FilterError:
        return []

    columns = {str(c) for c in df.columns}
    messages: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        operands = [node.left, *node.comparators]
        for left, right in zip(operands, operands[1:]):
            for col_node, value_node in ((left, right), (right, left)):
                if not isinstance(col_node, ast.Name):
                    continue
                col = placeholders.get(col_node.id, col_node.id)
                values = _literal_values(value_node)
                if col not in columns or values is None:
                    continue
                msg = _mismatch_message(col, df[col], values)
                if msg and msg not in messages:
                    messages.append(msg)
    return messages


def format_literal(value: Any) -> str:
    """Format a value the way it should be written in a filter expression."""
    if isinstance(value, str):
        return f'"{value}"' if '"' not in value else f"'{value}'"
    return repr(value.item() if hasattr(value, "item") else value)


def quote_column(name: str) -> str:
    """Return a column name as it should be written in a filter (backticked if needed)."""
    return name if name.isidentifier() else f"`{name}`"


def _literal_values(node: ast.AST) -> Optional[list[Any]]:
    if isinstance(node, ast.Constant):
        return [node.value]
    if isinstance(node, (ast.List, ast.Tuple)) and all(
        isinstance(elt, ast.Constant) for elt in node.elts
    ):
        return [elt.value for elt in node.elts]
    return None


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _mismatch_message(col: str, series: pd.Series, values: list[Any]) -> Optional[str]:
    kind = column_kind(series)
    shown = quote_column(col)
    if kind == "numeric":
        bad = next((v for v in values if isinstance(v, str)), None)
        if bad is not None:
            return (f"'{col}' is numeric but is compared with text \"{bad}\" — "
                    f"remove the quotes, e.g. {shown} == {bad}.")
    elif kind == "text":
        bad = next((v for v in values if _is_number(v)), None)
        sample = series.dropna().head(1000)
        if bad is not None and not sample.map(_is_number).any():
            return (f"'{col}' is a text column but is compared with the number {bad} — "
                    f"text values need quotes, e.g. {shown} == \"{bad}\".")
    elif kind == "datetime":
        bad = next((v for v in values if _is_number(v)), None)
        if bad is not None:
            return (f"'{col}' contains dates — compare with a date string, "
                    f"e.g. {shown} >= \"2024-01-01\", or use {shown}.dt.year == {bad}.")
    elif kind == "boolean":
        bad = next((v for v in values if isinstance(v, str)), None)
        if bad is not None:
            return f"'{col}' is True/False — compare without quotes, e.g. {shown} == True."
    return None


def _to_bool_mask(result: Any) -> pd.Series:
    error = FilterError(
        "The filter must evaluate to True/False for each row, "
        "e.g. time >= 0 or Country == \"USA\"."
    )
    if not isinstance(result, pd.Series):
        raise error
    if pd.api.types.is_bool_dtype(result):
        return result.fillna(False).astype(bool)
    # .str methods on columns with missing values return object dtype with NaN
    if result.dtype == object and result.dropna().map(lambda v: isinstance(v, (bool, np.bool_))).all():
        return result.map(lambda v: isinstance(v, (bool, np.bool_)) and bool(v)).astype(bool)
    raise error


def _check_unquoted_column_names(expr: str, columns: list[str]) -> None:
    """Catch column names with spaces that were typed without backticks."""
    unquoted = _BACKTICK_RE.sub("", expr)
    for col in columns:
        if not col.isidentifier() and " " in col and col in unquoted:
            raise FilterError(
                f"Column '{col}' contains spaces — wrap it in backticks: `{col}`."
            )


def _undefined_message(error: str, columns: list[str]) -> str:
    match = re.search(r"name '([^']+)' is not defined", error)
    if not match:
        return f"Could not evaluate filter: {error}"
    name = match.group(1)
    msg =(f"Unknown name '{name}'. If it is a text value, put it in quotes: \"{name}\". "
           f"If it is a column, check the spelling")
    close = difflib.get_close_matches(name, columns, n=1)
    if close:
        msg += f" (did you mean {quote_column(close[0])}?)"
    return msg + "."


def _type_mismatch_message(error: str, df: pd.DataFrame, referenced: set[str]) -> str:
    kinds = ", ".join(f"{c} is {column_kind(df[c])}" for c in sorted(referenced))
    msg = f"Type mismatch ({error})."
    if kinds:
        msg += f" Column types: {kinds}."
    return msg + " Text values need quotes; numbers and True/False do not."
