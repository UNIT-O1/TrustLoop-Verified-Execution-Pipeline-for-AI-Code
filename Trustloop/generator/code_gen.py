from typing import Optional

_REGISTRY: dict[str, callable] = {}

def register(name: str):
    def decorator(fn):
        _REGISTRY[name] = fn
        return fn
    return decorator

def get_supported_algorithms() -> list[str]:
    return sorted(_REGISTRY.keys())

def generate_code(algorithm: str) -> str:
    if algorithm not in _REGISTRY:
        raise ValueError(f"Unknown algorithm '{algorithm}'. Supported: {get_supported_algorithms()}")
    return _REGISTRY[algorithm]()

@register("Boolean AND")
def _boolean_and_code() -> str:
    return '''\
def boolean_and(a: bool, b: bool) -> bool:
    return a and b
'''
@register("GCD (Recursive)")
def _gcd_code() -> str:
    return '''\
def gcd(a: int, b: int) -> int:
    """Euclidean algorithm: gcd(a, b) = gcd(b, a % b)"""
    while b:
        a, b = b, a % b
    return a
'''

@register("Ariane 5 Safe Float-to-Int")
def _ariane_safe_code() -> str:
    return '''\
def safe_convert_64_to_16(val: float) -> int:
    """
    Prevents the 1996 Ariane 5 crash logic by checking bounds 
    before 64-bit float to 16-bit signed int conversion.
    """
    MAX_16 = 32767
    MIN_16 = -32768
    if val > MAX_16 or val < MIN_16:
        # In a real mission, this would trigger a hardware exception or backup
        raise ValueError("Critical Overflow: Value exceeds 16-bit range.")
    return int(val)
'''

@register("Factorial")
def _factorial_code() -> str:
    return '''\
def factorial(n: int) -> int:
    if n < 0: raise ValueError("n must be non-negative")
    if n == 0: return 1
    res = 1
    for i in range(1, n + 1):
        res *= i
    return res
'''

@register("Binary Search")
def _binary_search_code() -> str:
    return '''\
def binary_search(arr: list, target: int) -> int:
    assert arr == sorted(arr), "Precondition violated: array must be sorted."
    low: int = 0
    high: int = len(arr) - 1
    while low <= high:
        mid: int = low + (high - low) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
'''

@register("Linear Search")
def _linear_search_code() -> str:
    return '''\
def linear_search(arr: list, target: int) -> int:
    for index, element in enumerate(arr):
        if element == target:
            return index
    return -1
'''

@register("Bubble Sort")
def _bubble_sort_code() -> str:
    return '''\
def bubble_sort(arr: list) -> list:
    result = list(arr)
    n = len(result)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True
        if not swapped:
            break
    assert result == sorted(arr), "Postcondition violated: output must be sorted."
    return result
'''

@register("Insertion Sort")
def _insertion_sort_code() -> str:
    return '''\
def insertion_sort(arr: list) -> list:
    result = list(arr)
    n = len(result)
    for i in range(1, n):
        key = result[i]
        j = i - 1
        while j >= 0 and result[j] > key:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = key
    assert result == sorted(arr), "Postcondition violated: output must be sorted."
    return result
'''

@register("Prime Check (Buggy)")
def _prime_check_code() -> str:
    return '''\
def is_prime_buggy(n: int) -> bool:
    """A buggy primality test optimized to check only up to n/3."""
    if n < 2: return False
    for d in range(2, int(n/3) + 1):
        if n % d == 0: return False
    return True
'''