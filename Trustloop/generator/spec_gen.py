from typing import TypedDict

class FormalSpec(TypedDict):
    algorithm: str
    pre: str
    post: str
    invariant: str
    complexity: dict[str, str]
    notes: str

_SPEC_REGISTRY: dict[str, FormalSpec] = {}

def register_spec(name: str, spec: FormalSpec) -> None:
    _SPEC_REGISTRY[name] = spec

def get_spec(algorithm: str) -> FormalSpec:
    if algorithm not in _SPEC_REGISTRY:
        raise ValueError(f"No specification found for '{algorithm}'.")
    return _SPEC_REGISTRY[algorithm]

register_spec("Binary Search", FormalSpec(
    algorithm="Binary Search",
    pre="arr is sorted in non-decreasing order.",
    post="Returns index i where arr[i]==target, else -1.",
    invariant="If target in arr, it is in arr[low..high].",
    complexity={"time_best": "O(1)", "time_average": "O(log n)", "time_worst": "O(log n)", "space": "O(1)"},
    notes="Fails if input is unsorted."
))

register_spec("Linear Search", FormalSpec(
    algorithm="Linear Search",
    pre="None (works on any list).",
    post="Returns FIRST index where arr[i]==target, else -1.",
    invariant="Target is not in arr[0..k-1].",
    complexity={"time_best": "O(1)", "time_average": "O(n)", "time_worst": "O(n)", "space": "O(1)"},
    notes="Universal but slow."
))

register_spec("GCD (Recursive)", FormalSpec(
    algorithm="GCD (Recursive)",
    pre="a and b are non-negative integers.",
    post="Returns the largest integer k such that k|a and k|b.",
    invariant="gcd(a, b) == gcd(orig_a, orig_b)",
    complexity={"time": "O(log(min(a,b)))", "space": "O(1)"},
    notes="Based on Euclidean geometry."
))

register_spec("Ariane 5 Safe Float-to-Int", FormalSpec(
    algorithm="Ariane 5 Safe Float-to-Int",
    pre="Input is a 64-bit floating point number.",
    post="Result is a signed 16-bit integer within [-32768, 32767].",
    invariant="N/A",
    complexity={"time": "O(1)", "space": "O(1)"},
    notes="Formal verification ensures no value can bypass the range check."
))

register_spec("Boolean AND", FormalSpec(
    algorithm="Boolean AND",
    pre="a and b are boolean values.",
    post="Returns True iff both a and b are True.",
    invariant="N/A",
    complexity={"time": "O(1)", "space": "O(1)"},
    notes="Fundamental boolean logic."
))

register_spec("Factorial", FormalSpec(
    algorithm="Factorial",
    pre="n is an integer where n >= 0.",
    post="Returns n! (product of all integers from 1 to n).",
    invariant="res = i!",
    complexity={"time": "O(n)", "space": "O(1)"},
    notes="Iterative implementation."
))

register_spec("Bubble Sort", FormalSpec(
    algorithm="Bubble Sort",
    pre="arr is comparable.",
    post="Returns sorted permutation.",
    invariant="Last i elements are sorted.",
    complexity={"time_best": "O(n)", "time_average": "O(n²)", "time_worst": "O(n²)", "space": "O(n)"},
    notes="Teaching algorithm."
))

register_spec("Insertion Sort", FormalSpec(
    algorithm="Insertion Sort",
    pre="arr is comparable.",
    post="Returns sorted permutation.",
    invariant="First i elements are sorted.",
    complexity={"time_best": "O(n)", "time_average": "O(n²)", "time_worst": "O(n²)", "space": "O(n)"},
    notes="Fast for small n."
))

register_spec("Prime Check (Buggy)", FormalSpec(
    algorithm="Prime Check (Buggy)",
    pre="n is a non-negative integer: n ≥ 0.",
    post="Returns True iff n is prime (no divisors in [2, n-1]).",
    invariant="Target has no divisors in [2, current_d].",
    complexity={"time_best": "O(1)", "time_average": "O(n)", "time_worst": "O(n)", "space": "O(1)"},
    notes="This algorithm incorrectly bounds the search at n/3. Z3 will mathematically prove this insufficiency."
))