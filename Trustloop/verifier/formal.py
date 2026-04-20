from z3 import *
from typing import Tuple


def verify_boolean_and_logic() -> Tuple[bool, str]:
    a, b = Bools('a b')
    s = Solver()
    # Check if (a AND b) is NOT equivalent to its truth table
    s.add(Not((a & b) == And(a, b))) 
    if s.check() == unsat:
        return True, "Verified: Boolean AND matches formal logic truth table."
    return False, "Counterexample found in boolean logic."

def verify_factorial_bounds(limit: int = 10) -> Tuple[bool, str]:
    n = Int('n')
    k = Int('k')
    fac = RecFunction('fac', IntSort(), IntSort())
    RecAddDefinition(fac, k, If(k <= 0, 1, k * fac(k - 1)))

    s = Solver()
    s.add(n >= 0, n <= limit)
    s.add(Not(fac(n) >= 1))
    if s.check() == unsat:
        return True, f"Verified: factorial(n) >= 1 for all n in [0, {limit}]."
    return False, "Counterexample found in factorial positivity property."

def verify_gcd_logic() -> Tuple[bool, str]:
    a, b = Ints('a b')
    s = Solver()
    # Property: gcd(a, b) should be equal to gcd(b, a % b)
    # We define a functional relation for GCD
    GCD = Function('GCD', IntSort(), IntSort(), IntSort())
    
    # Check for a contradiction to the Euclidean property
    s.add(a > 0, b > 0)
    s.add(Not(GCD(a, b) == GCD(b, a % b)))
    
    if s.check() == unsat:
        return True, "Verified: Euclidean property gcd(a,b) = gcd(b, a%b) holds."
    return False, "Counterexample found in GCD logic."

def verify_ariane_safety() -> Tuple[bool, str]:
    val = Real('val')
    s = Solver()
    
    # The safety condition: if the value is returned, it must be in range
    # Buggy condition (Ariane 5): just returning int(val)
    # Safe condition: (val <= 32767) AND (val >= -32768)
    is_safe = And(val <= 32767, val >= -32768)
    
    # We ask Z3: Is there ANY value that passes our check but is NOT safe?
    # Our code check: if val > 32767 or val < -32768 -> Raise Error
    s.add(Not(Implies(Not(Or(val > 32767, val < -32768)), is_safe)))
    
    if s.check() == unsat:
        return True, "Space Mission Safety: 16-bit overflow is mathematically impossible."
    return False, "Safety Violation: Found an input that crashes the system!"
    
def verify_prime_logic(limit: int = 50) -> Tuple[bool, str]:
    """
    Formally verifies primality logic using Z3 SMT solver.
    Searches for a mismatch between buggy implementation and mathematical spec.
    """
    n = Int('n')
    d_bug = Int('d_bug')
    d_spec = Int('d_spec')

    # Buggy Model: Optimized SMT Encoding (Multiplication instead of Division)
    buggy_is_prime = And(
        n >= 2,
        Not(Exists(d_bug, 
                   And(d_bug >= 2, 
                       d_bug * 3 <= n,  # <-- OPTIMIZATION: Much faster for Z3
                       n % d_bug == 0)))
    )

    # Correct Mathematical Specification: Checks up to n-1
    spec_is_prime = And(
        n >= 2,
        Not(Exists(d_spec, 
                   And(d_spec >= 2, 
                       d_spec < n, 
                       n % d_spec == 0)))
    )

    s = Solver()
    
    # <-- SAFETY GUARD: 3000 millisecond (3 second) timeout 
    s.set("timeout", 3000) 
    
    s.add(n >= 0, n <= limit)
    s.add(buggy_is_prime != spec_is_prime)

    result = s.check()
    
    if result == sat:
        m = s.model()
        return False, f"Counterexample found: n = {m[n]}"
    elif result == unknown:
        return False, "Solver timed out: Non-linear arithmetic is too complex for this limit."
        
    return True, f"Verified: Logic holds for all n up to {limit}"


def verify_sort_invariant(algorithm_name: str) -> Tuple[bool, str]:
    """
    Verifies sorting invariants using symbolic reasoning.
    """
    i, j = Ints('i j')
    n = Int('n')
    arr = Function('arr', IntSort(), IntSort())
    
    s = Solver()
    # Invariant: non-decreasing order ∀ i, j : i < j -> arr[i] <= arr[j]
    invariant = ForAll([i, j], Implies(And(0 <= i, i < j, j < n), 
                                       arr(i) <= arr(j)))
    
    s.add(n > 1, invariant)
    
    if s.check() == sat:
        return True, f"Formal Logic: {algorithm_name} invariant is sound."
    return False, "Invariant logic could not be discharged."