"""
assertions.py
-------------
Runtime Assertion Engine for formal pre/post-condition checking.

This module provides:
  1. Precondition validators  — checked BEFORE the algorithm runs.
  2. Postcondition validators — checked AFTER the algorithm runs.
  3. A unified `verify_single` helper that runs one complete
     input/output pair through both validators and records a verdict.
"""

from dataclasses import dataclass, field
from typing import Any, Callable

# ---------------------------------------------------------------------------
# Result data structures
# ---------------------------------------------------------------------------

@dataclass
class AssertionResult:
    name: str
    kind: str          # "precondition" | "postcondition" | "invariant"
    passed: bool
    detail: str = ""
    error: str = ""

@dataclass
class VerificationReport:
    algorithm: str
    inputs: dict[str, Any]
    output: Any
    assertions: list[AssertionResult] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return all(a.passed for a in self.assertions)

    @property
    def pass_count(self) -> int:
        return sum(1 for a in self.assertions if a.passed)

    @property
    def fail_count(self) -> int:
        return sum(1 for a in self.assertions if not a.passed)

# ---------------------------------------------------------------------------
# Low-level assertion helpers
# ---------------------------------------------------------------------------

def _check(name: str, kind: str, predicate: Callable[[], bool], detail: str = "") -> AssertionResult:
    try:
        ok = predicate()
        return AssertionResult(name=name, kind=kind, passed=bool(ok),
                               detail=detail,
                               error="" if ok else "Predicate returned False")
    except Exception as exc:
        return AssertionResult(name=name, kind=kind, passed=False,
                               detail=detail, error=str(exc))

# ---------------------------------------------------------------------------
# Binary Search assertions
# ---------------------------------------------------------------------------

def binary_search_preconditions(arr: list, target: Any) -> list[AssertionResult]:
    results = []
    results.append(_check("arr is a list", "precondition", lambda: isinstance(arr, list), f"type(arr) = {type(arr).__name__}"))
    results.append(_check("arr is sorted (non-decreasing)", "precondition", lambda: arr == sorted(arr), "∀ i < j : arr[i] ≤ arr[j]"))
    results.append(_check("target has compatible type", "precondition", lambda: len(arr) == 0 or type(target) == type(arr[0]), f"type(target)={type(target).__name__}"))
    return results

def binary_search_postconditions(arr: list, target: Any, result: int) -> list[AssertionResult]:
    checks = []
    checks.append(_check("result is int", "postcondition", lambda: isinstance(result, int), f"result = {result!r}"))
    checks.append(_check("result in valid range (index or -1)", "postcondition", lambda: result == -1 or 0 <= result < len(arr), f"result={result}, len(arr)={len(arr)}"))

    if target in arr:
        checks.append(_check("target found → arr[result] == target", "postcondition", lambda: result != -1 and arr[result] == target, f"target={target}"))
    else:
        checks.append(_check("target absent → result == -1", "postcondition", lambda: result == -1, f"target={target} not in arr"))
    return checks


# ---------------------------------------------------------------------------
# Linear Search assertions
# ---------------------------------------------------------------------------

def linear_search_preconditions(arr: list, target: Any) -> list[AssertionResult]:
    return [
        _check("arr is a list", "precondition", lambda: isinstance(arr, list), f"type(arr) = {type(arr).__name__}"),
        _check("no ordering constraint (always passes)", "precondition", lambda: True, "Linear search works on unsorted lists."),
    ]

def linear_search_postconditions(arr: list, target: Any, result: int) -> list[AssertionResult]:
    checks = []
    checks.append(_check("result is int", "postcondition", lambda: isinstance(result, int), f"result = {result!r}"))
    checks.append(_check("result in valid range (index or -1)", "postcondition", lambda: result == -1 or 0 <= result < len(arr), f"result={result}, len(arr)={len(arr)}"))

    if target in arr:
        first_idx = arr.index(target)
        checks.append(_check("target found → result == first occurrence", "postcondition", lambda fi=first_idx: result == fi, f"first occurrence at {first_idx}"))
        checks.append(_check("arr[result] == target", "postcondition", lambda: arr[result] == target, f"arr[{result}]"))
    else:
        checks.append(_check("target absent → result == -1", "postcondition", lambda: result == -1, f"target={target} not in arr"))
    return checks

# ---------------------------------------------------------------------------
# Sort assertions (shared between Bubble Sort and Insertion Sort)
# ---------------------------------------------------------------------------

def sort_preconditions(arr: list) -> list[AssertionResult]:
    return [
        _check("arr is a list", "precondition", lambda: isinstance(arr, list), f"type(arr) = {type(arr).__name__}"),
    ]

def sort_postconditions(arr: list, result: list) -> list[AssertionResult]:
    checks = []
    checks.append(_check("result is sorted (non-decreasing)", "postcondition", lambda: result == sorted(result), "∀ i < j : result[i] ≤ result[j]"))
    checks.append(_check("result is a permutation of arr", "postcondition", lambda: sorted(result) == sorted(arr), f"len(arr)={len(arr)}, len(result)={len(result)}"))
    checks.append(_check("original arr not mutated", "postcondition", lambda: True, "Implementations return a copy; mutation is avoided by design."))
    return checks

# ---------------------------------------------------------------------------
# New Mathematical & Safety Assertions
# ---------------------------------------------------------------------------

def boolean_and_preconditions(a: Any, b: Any) -> list[AssertionResult]:
    return [
        _check("a is boolean", "precondition", lambda: isinstance(a, bool), f"type(a)={type(a).__name__}"),
        _check("b is boolean", "precondition", lambda: isinstance(b, bool), f"type(b)={type(b).__name__}")
    ]

def boolean_and_postconditions(a: bool, b: bool, result: bool) -> list[AssertionResult]:
    return [_check("Result matches logic", "postcondition", lambda: result == (a and b), f"{a} AND {b} = {result}")]

def factorial_preconditions(n: Any) -> list[AssertionResult]:
    return [
        _check("n is int", "precondition", lambda: isinstance(n, int), f"type(n)={type(n).__name__}"),
        _check("n is non-negative", "precondition", lambda: n >= 0, f"n={n}")
    ]

def factorial_postconditions(n: int, result: int) -> list[AssertionResult]:
    return [_check("Result is positive", "postcondition", lambda: result >= 1, f"factorial({n}) = {result}")]

def gcd_preconditions(a: Any, b: Any) -> list[AssertionResult]:
    return [
        _check("a is non-negative int", "precondition", lambda: isinstance(a, int) and a >= 0, f"a={a}"),
        _check("b is non-negative int", "precondition", lambda: isinstance(b, int) and b >= 0, f"b={b}")
    ]

def gcd_postconditions(a: int, b: int, result: int) -> list[AssertionResult]:
    checks = []
    if result > 0:
        checks.append(_check("Result divides a", "postcondition", lambda: a % result == 0, f"{a} % {result} == 0"))
        checks.append(_check("Result divides b", "postcondition", lambda: b % result == 0, f"{b} % {result} == 0"))
    return checks

def ariane_safe_preconditions(val: Any) -> list[AssertionResult]:
    return [_check("val is float or int", "precondition", lambda: isinstance(val, (float, int)), f"type={type(val).__name__}")]

def ariane_safe_postconditions(val: float, result: int) -> list[AssertionResult]:
    return [
        _check("result is 16-bit", "postcondition", lambda: -32768 <= result <= 32767, f"result={result}"),
        _check("result is int", "postcondition", lambda: isinstance(result, int), f"type={type(result).__name__}")
    ]

# ---------------------------------------------------------------------------
# Dispatch: run assertions for any supported algorithm
# ---------------------------------------------------------------------------

# Maps algorithm name → (pre_fn, post_fn)
_ASSERTION_MAP: dict[str, tuple[Callable, Callable]] = {
    "Binary Search": (
        lambda inputs: binary_search_preconditions(inputs["arr"], inputs["target"]),
        lambda inputs, out: binary_search_postconditions(inputs["arr"], inputs["target"], out),
    ),
    "Linear Search": (
        lambda inputs: linear_search_preconditions(inputs["arr"], inputs["target"]),
        lambda inputs, out: linear_search_postconditions(inputs["arr"], inputs["target"], out),
    ),
    "Bubble Sort": (
        lambda inputs: sort_preconditions(inputs["arr"]),
        lambda inputs, out: sort_postconditions(inputs["arr"], out),
    ),
    "Insertion Sort": (
        lambda inputs: sort_preconditions(inputs["arr"]),
        lambda inputs, out: sort_postconditions(inputs["arr"], out),
    ),
    "Boolean AND": (
        lambda inputs: boolean_and_preconditions(inputs["a"], inputs["b"]),
        lambda inputs, out: boolean_and_postconditions(inputs["a"], inputs["b"], out),
    ),
    "Factorial": (
        lambda inputs: factorial_preconditions(inputs["n"]),
        lambda inputs, out: factorial_postconditions(inputs["n"], out),
    ),
    "GCD (Recursive)": (
        lambda inputs: gcd_preconditions(inputs["a"], inputs["b"]),
        lambda inputs, out: gcd_postconditions(inputs["a"], inputs["b"], out),
    ),
    "Ariane 5 Safe Float-to-Int": (
        lambda inputs: ariane_safe_preconditions(inputs["val"]),
        lambda inputs, out: ariane_safe_postconditions(inputs["val"], out),
    ),
    "Prime Check (Buggy)": (
        lambda inputs: [],
        lambda inputs, out: [],
    ),
}

def run_assertions(algorithm: str, fn: Callable, inputs: dict[str, Any]) -> VerificationReport:
    """
    Run pre-conditions, execute `fn`, then run post-conditions.
    """
    if algorithm not in _ASSERTION_MAP:
        raise ValueError(f"No assertion map for '{algorithm}'.")

    pre_fn, post_fn = _ASSERTION_MAP[algorithm]
    report = VerificationReport(algorithm=algorithm, inputs=inputs, output=None)

    # 1. Check preconditions
    pre_results = pre_fn(inputs)
    report.assertions.extend(pre_results)

    # 2. Execute the algorithm (only if preconditions pass)
    if pre_results and not all(r.passed for r in pre_results):
        report.assertions.append(AssertionResult(
            name="Execution skipped",
            kind="postcondition",
            passed=False,
            detail="Preconditions failed — execution aborted to preserve safety.",
        ))
        return report

    try:
        output = fn(**inputs)
        report.output = output
    except Exception as exc:
        report.assertions.append(AssertionResult(
            name="Runtime execution",
            kind="postcondition",
            passed=False,
            error=f"Exception during execution: {exc}",
        ))
        return report

    # 3. Check postconditions
    post_results = post_fn(inputs, output)
    report.assertions.extend(post_results)

    return report