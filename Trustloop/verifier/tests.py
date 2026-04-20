"""
tests.py
--------
Property-Based Testing using the Hypothesis library.

Property-based testing (PBT) differs from unit testing in a fundamental way:
instead of supplying SPECIFIC inputs, we declare PROPERTIES that must hold for
ALL inputs from a given domain, and let Hypothesis generate hundreds of random
examples — including edge cases the programmer might not think of.

This is a step closer to formal verification than classical unit testing.

Each test suite returns a list of TestResult objects so the Streamlit UI can
display structured pass/fail information without needing pytest.
"""

from dataclasses import dataclass, field
from typing import Callable, Any
import traceback

from hypothesis import given, settings, HealthCheck, assume
from hypothesis import strategies as st


# ---------------------------------------------------------------------------
# Result data structure
# ---------------------------------------------------------------------------

@dataclass
class TestResult:
    name: str
    kind: str          # "property" | "edge_case" | "regression"
    passed: bool
    detail: str = ""
    counterexample: str = ""
    num_examples: int = 0


@dataclass
class TestSuiteReport:
    algorithm: str
    results: list[TestResult] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return all(r.passed for r in self.results)

    @property
    def pass_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def fail_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)


# ---------------------------------------------------------------------------
# Helper: run a Hypothesis test and capture the verdict
# ---------------------------------------------------------------------------

def _run_hypothesis(name: str, kind: str, detail: str,
                    test_fn: Callable, num_examples: int = 100) -> TestResult:
    """
    Call `test_fn()` (a @given-decorated function) and return a TestResult.
    Hypothesis raises on the first falsifying example; we catch and record it.
    """
    try:
        test_fn()
        return TestResult(name=name, kind=kind, passed=True,
                          detail=detail, num_examples=num_examples)
    except Exception as exc:
        return TestResult(name=name, kind=kind, passed=False,
                          detail=detail,
                          counterexample=str(exc)[:400],
                          num_examples=num_examples)


def _run_edge(name: str, kind: str, detail: str,
              test_fn: Callable) -> TestResult:
    """Run a deterministic edge-case test (no Hypothesis)."""
    try:
        test_fn()
        return TestResult(name=name, kind=kind, passed=True, detail=detail)
    except Exception as exc:
        return TestResult(name=name, kind=kind, passed=False,
                          detail=detail, counterexample=str(exc)[:400])


# ---------------------------------------------------------------------------
# Binary Search Test Suite
# ---------------------------------------------------------------------------

def run_binary_search_tests(fn: Callable) -> TestSuiteReport:
    """
    Property-based and edge-case tests for binary_search(arr, target) -> int.

    Properties verified:
      P1. Correctness    — returned index satisfies arr[i] == target.
      P2. Completeness   — target present ⟹ result ≠ -1.
      P3. Soundness      — result == -1 ⟹ target ∉ arr.
      P4. Stability      — pure function; calling twice gives same result.
      P5. Sorted prefix  — result found even when array has many duplicates.
    """
    report = TestSuiteReport(algorithm="Binary Search")
    N = 150  # number of Hypothesis examples per property

    # --- P1 + P2 + P3: Core correctness ---
    @settings(max_examples=N, suppress_health_check=[HealthCheck.too_slow])
    @given(
        st.lists(st.integers(min_value=-1000, max_value=1000),
                 min_size=0, max_size=50).map(sorted),
        st.integers(min_value=-1000, max_value=1000),
    )
    def prop_correctness(arr, target):
        result = fn(arr, target)
        if target in arr:
            assert result != -1, \
                f"P2 violated: target {target} is in arr but result == -1"
            assert 0 <= result < len(arr), \
                f"P1 violated: result {result} out of range [0, {len(arr)})"
            assert arr[result] == target, \
                f"P1 violated: arr[{result}]={arr[result]} ≠ target={target}"
        else:
            assert result == -1, \
                f"P3 violated: target {target} absent but result={result} ≠ -1"

    report.results.append(_run_hypothesis(
        "P1+P2+P3: Correctness, completeness, soundness",
        "property",
        "For all sorted arrays and all targets: result is correct index or -1.",
        prop_correctness, N,
    ))

    # --- P4: Referential transparency (pure function) ---
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(
        st.lists(st.integers(-500, 500), min_size=0, max_size=30).map(sorted),
        st.integers(-500, 500),
    )
    def prop_pure(arr, target):
        r1 = fn(arr, target)
        r2 = fn(arr, target)
        assert r1 == r2, f"P4 violated: two calls returned {r1} and {r2}"

    report.results.append(_run_hypothesis(
        "P4: Referential transparency",
        "property",
        "Calling binary_search twice with same inputs yields same result.",
        prop_pure, 50,
    ))

    # --- P5: Duplicates — target must be found ---
    @settings(max_examples=80, suppress_health_check=[HealthCheck.too_slow])
    @given(
        st.lists(st.integers(-100, 100), min_size=2, max_size=40).map(sorted),
    )
    def prop_duplicates(arr):
        # Pick an element we KNOW is in the array
        target = arr[len(arr) // 2]
        result = fn(arr, target)
        assert result != -1, \
            f"P5 violated: {target} is in {arr} but result == -1"
        assert arr[result] == target, \
            f"P5 violated: arr[{result}]={arr[result]} ≠ {target}"

    report.results.append(_run_hypothesis(
        "P5: Duplicates — element guaranteed present",
        "property",
        "When target is taken directly from arr, search must find it.",
        prop_duplicates, 80,
    ))

    # --- Edge cases (deterministic) ---
    def edge_empty():
        assert fn([], 42) == -1, "Empty list should return -1"

    report.results.append(_run_edge(
        "EC1: Empty list → -1", "edge_case",
        "binary_search([], 42) must return -1.", edge_empty,
    ))

    def edge_single_found():
        assert fn([7], 7) == 0, "Single-element list, target present → index 0"

    report.results.append(_run_edge(
        "EC2: Single element (found) → 0", "edge_case",
        "binary_search([7], 7) must return 0.", edge_single_found,
    ))

    def edge_single_not_found():
        assert fn([7], 99) == -1, "Single-element list, target absent → -1"

    report.results.append(_run_edge(
        "EC3: Single element (not found) → -1", "edge_case",
        "binary_search([7], 99) must return -1.", edge_single_not_found,
    ))

    def edge_first_element():
        arr = [1, 3, 5, 7, 9]
        r = fn(arr, 1)
        assert r == 0, f"First element: expected 0, got {r}"

    report.results.append(_run_edge(
        "EC4: Target is first element", "edge_case",
        "binary_search([1,3,5,7,9], 1) must return 0.", edge_first_element,
    ))

    def edge_last_element():
        arr = [1, 3, 5, 7, 9]
        r = fn(arr, 9)
        assert arr[r] == 9, f"Last element: arr[{r}]={arr[r] if r != -1 else '?'} ≠ 9"

    report.results.append(_run_edge(
        "EC5: Target is last element", "edge_case",
        "binary_search([1,3,5,7,9], 9) must return arr[result]==9.",
        edge_last_element,
    ))

    def edge_all_same():
        arr = [5, 5, 5, 5, 5]
        r = fn(arr, 5)
        assert r != -1 and arr[r] == 5, "All same elements, target present"
        r2 = fn(arr, 6)
        assert r2 == -1, "All same elements, target absent"

    report.results.append(_run_edge(
        "EC6: All identical elements", "edge_case",
        "binary_search([5,5,5,5], 5)→found; binary_search([5,5,5,5], 6)→-1.",
        edge_all_same,
    ))

    def edge_negative_numbers():
        arr = sorted([-10, -5, -3, -1, 0, 2])
        r = fn(arr, -5)
        assert r != -1 and arr[r] == -5, "Negative numbers must work"

    report.results.append(_run_edge(
        "EC7: Negative integers", "edge_case",
        "Search works correctly on arrays with negative values.",
        edge_negative_numbers,
    ))

    return report


# ---------------------------------------------------------------------------
# Linear Search Test Suite
# ---------------------------------------------------------------------------

def run_linear_search_tests(fn: Callable) -> TestSuiteReport:
    """
    Property-based and edge-case tests for linear_search(arr, target) -> int.

    Properties verified:
      P1. Correctness    — arr[result] == target when result ≠ -1.
      P2. First-occurrence guarantee — result == min index of target.
      P3. Soundness      — result == -1 ⟹ target ∉ arr.
      P4. Works on unsorted arrays.
    """
    report = TestSuiteReport(algorithm="Linear Search")
    N = 150

    # --- P1 + P3: Correctness and soundness (unsorted arrays) ---
    @settings(max_examples=N, suppress_health_check=[HealthCheck.too_slow])
    @given(
        st.lists(st.integers(-1000, 1000), min_size=0, max_size=60),
        st.integers(-1000, 1000),
    )
    def prop_correctness_unsorted(arr, target):
        result = fn(arr, target)
        if target in arr:
            assert result != -1, \
                f"P1 violated: target {target} is in arr but result == -1"
            assert 0 <= result < len(arr), \
                f"P1 violated: result {result} out of range"
            assert arr[result] == target, \
                f"P1 violated: arr[{result}]={arr[result]} ≠ {target}"
        else:
            assert result == -1, \
                f"P3 violated: target absent but result={result}"

    report.results.append(_run_hypothesis(
        "P1+P3: Correctness on arbitrary (unsorted) arrays",
        "property",
        "For ANY list and any target: result is correct first index or -1.",
        prop_correctness_unsorted, N,
    ))

    # --- P2: First-occurrence guarantee ---
    # Strategy: build arr first, then draw target FROM arr so it is guaranteed
    # present. This avoids the over-filtering problem with assume(target in arr).
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(
        st.lists(st.integers(-200, 200), min_size=1, max_size=50).flatmap(
            lambda lst: st.tuples(st.just(lst), st.sampled_from(lst))
        )
    )
    def prop_first_occurrence(arr_and_target):
        arr, target = arr_and_target
        result = fn(arr, target)
        expected = arr.index(target)   # Python's built-in returns first index
        assert result == expected, \
            f"P2 violated: expected first occurrence at {expected}, got {result}"

    report.results.append(_run_hypothesis(
        "P2: First-occurrence guarantee",
        "property",
        "When duplicates exist, result must equal the minimum matching index.",
        prop_first_occurrence, 100,
    ))

    # --- P4: Works on sorted arrays too (regression vs binary search) ---
    @settings(max_examples=80, suppress_health_check=[HealthCheck.too_slow])
    @given(
        st.lists(st.integers(-500, 500), min_size=0, max_size=40).map(sorted),
        st.integers(-500, 500),
    )
    def prop_sorted_arrays(arr, target):
        result = fn(arr, target)
        if target in arr:
            assert result != -1 and arr[result] == target
        else:
            assert result == -1

    report.results.append(_run_hypothesis(
        "P4: Correct on sorted arrays too",
        "property",
        "Linear search is universally applicable — sorted inputs are fine.",
        prop_sorted_arrays, 80,
    ))

    # --- Edge cases ---
    report.results.append(_run_edge(
        "EC1: Empty list → -1", "edge_case",
        "linear_search([], 42) must return -1.",
        lambda: (lambda r: None if r == -1 else (_ for _ in ()).throw(
            AssertionError(f"Expected -1, got {r}")))(fn([], 42)),
    ))

    def edge_single_found():
        assert fn([99], 99) == 0

    report.results.append(_run_edge(
        "EC2: Single element (found) → 0", "edge_case",
        "linear_search([99], 99) must return 0.", edge_single_found,
    ))

    def edge_single_not_found():
        assert fn([99], 0) == -1

    report.results.append(_run_edge(
        "EC3: Single element (not found) → -1", "edge_case",
        "linear_search([99], 0) must return -1.", edge_single_not_found,
    ))

    def edge_duplicates_first():
        arr = [3, 1, 3, 3, 2]
        r = fn(arr, 3)
        assert r == 0, f"First occurrence of 3 is index 0, got {r}"

    report.results.append(_run_edge(
        "EC4: Duplicates — returns FIRST index", "edge_case",
        "linear_search([3,1,3,3,2], 3) must return 0 (first occurrence).",
        edge_duplicates_first,
    ))

    def edge_target_at_end():
        arr = [1, 2, 3, 4, 5]
        r = fn(arr, 5)
        assert r == 4, f"Target at last position: expected 4, got {r}"

    report.results.append(_run_edge(
        "EC5: Target at last position", "edge_case",
        "linear_search([1,2,3,4,5], 5) must return 4.", edge_target_at_end,
    ))

    def edge_unsorted():
        arr = [5, 3, 8, 1, 9, 2]
        r = fn(arr, 9)
        assert r == 4, f"Unsorted: expected index 4, got {r}"

    report.results.append(_run_edge(
        "EC6: Unsorted array (linear search advantage)", "edge_case",
        "linear_search([5,3,8,1,9,2], 9) must return 4.", edge_unsorted,
    ))

    return report


# ---------------------------------------------------------------------------
# Sort Test Suites (shared helper)
# ---------------------------------------------------------------------------

def _run_sort_tests(algorithm: str, fn: Callable) -> TestSuiteReport:
    """Shared property suite for sorting algorithms."""
    report = TestSuiteReport(algorithm=algorithm)
    N = 120

    @settings(max_examples=N, suppress_health_check=[HealthCheck.too_slow])
    @given(st.lists(st.integers(-1000, 1000), min_size=0, max_size=60))
    def prop_sorted_output(arr):
        result = fn(arr)
        assert result == sorted(result), \
            f"Output not sorted: {result[:10]}..."

    report.results.append(_run_hypothesis(
        "P1: Output is sorted", "property",
        "∀ arr: fn(arr) is in non-decreasing order.", prop_sorted_output, N,
    ))

    @settings(max_examples=N, suppress_health_check=[HealthCheck.too_slow])
    @given(st.lists(st.integers(-1000, 1000), min_size=0, max_size=60))
    def prop_permutation(arr):
        result = fn(arr)
        assert sorted(result) == sorted(arr), \
            "Output is not a permutation of input"

    report.results.append(_run_hypothesis(
        "P2: Output is a permutation of input", "property",
        "∀ arr: multiset(fn(arr)) == multiset(arr).", prop_permutation, N,
    ))

    @settings(max_examples=N, suppress_health_check=[HealthCheck.too_slow])
    @given(st.lists(st.integers(-1000, 1000), min_size=0, max_size=60))
    def prop_no_mutation(arr):
        original = list(arr)
        fn(arr)
        assert arr == original, "Input array was mutated"

    report.results.append(_run_hypothesis(
        "P3: Input array not mutated", "property",
        "fn(arr) must not modify arr in-place.", prop_no_mutation, N,
    ))

    def edge_empty():
        assert fn([]) == []

    report.results.append(_run_edge("EC1: Empty list", "edge_case",
                                    "fn([]) must return [].", edge_empty))

    def edge_single():
        assert fn([42]) == [42]

    report.results.append(_run_edge("EC2: Single element", "edge_case",
                                    "fn([42]) must return [42].", edge_single))

    def edge_already_sorted():
        arr = [1, 2, 3, 4, 5]
        assert fn(arr) == arr

    report.results.append(_run_edge("EC3: Already sorted", "edge_case",
                                    "Sorted input must be returned as-is.",
                                    edge_already_sorted))

    def edge_reverse_sorted():
        arr = [5, 4, 3, 2, 1]
        assert fn(arr) == [1, 2, 3, 4, 5]

    report.results.append(_run_edge("EC4: Reverse sorted", "edge_case",
                                    "fn([5,4,3,2,1]) must return [1,2,3,4,5].",
                                    edge_reverse_sorted))

    def edge_all_same():
        arr = [7, 7, 7, 7]
        assert fn(arr) == [7, 7, 7, 7]

    report.results.append(_run_edge("EC5: All identical elements", "edge_case",
                                    "fn([7,7,7,7]) must return [7,7,7,7].",
                                    edge_all_same))

    return report


def run_bubble_sort_tests(fn: Callable) -> TestSuiteReport:
    return _run_sort_tests("Bubble Sort", fn)


def run_insertion_sort_tests(fn: Callable) -> TestSuiteReport:
    return _run_sort_tests("Insertion Sort", fn)


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

_TEST_RUNNERS: dict[str, Callable] = {
    "Binary Search":  run_binary_search_tests,
    "Linear Search":  run_linear_search_tests,
    "Bubble Sort":    run_bubble_sort_tests,
    "Insertion Sort": run_insertion_sort_tests,
    # ADDED FOR Z3 FORMAL PROOF DEMO (Returns an empty report to avoid crashing)
    "Prime Check (Buggy)": lambda fn: TestSuiteReport(algorithm="Prime Check (Buggy)"),
    "Boolean AND": lambda fn: TestSuiteReport(algorithm="Boolean AND"),
    "Factorial": lambda fn: TestSuiteReport(algorithm="Factorial"),
    "GCD (Recursive)": lambda fn: TestSuiteReport(algorithm="GCD (Recursive)"),
    "Ariane 5 Safe Float-to-Int": lambda fn: TestSuiteReport(algorithm="Ariane 5 Safe Float-to-Int"),
}


def run_tests(algorithm: str, fn: Callable) -> TestSuiteReport:
    """
    Run the full property-based test suite for `algorithm` against `fn`.

    Parameters
    ----------
    algorithm : str      — name of the algorithm.
    fn        : Callable — the actual implementation to test.

    Returns
    -------
    TestSuiteReport with all test results.
    """
    if algorithm not in _TEST_RUNNERS:
        raise ValueError(f"No test suite for '{algorithm}'.")
    return _TEST_RUNNERS[algorithm](fn)