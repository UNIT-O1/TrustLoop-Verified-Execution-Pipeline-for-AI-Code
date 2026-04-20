# 🔬 Verified AI-Assisted Code Generation for Fundamental Algorithms

> A research-grade demonstration of lightweight formal verification combined with
> AI-assisted code generation, property-based testing, and runtime assertion checking.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [File Structure](#file-structure)
4. [What is Verification?](#what-is-verification)
5. [Testing vs Verification](#testing-vs-verification)
6. [Supported Algorithms](#supported-algorithms)
7. [Installation & Running](#installation--running)
8. [System Walkthrough](#system-walkthrough)
9. [Limitations](#limitations)
10. [Future Improvements](#future-improvements)
11. [References](#references)

---

## Project Overview

This project demonstrates how **formal methods concepts** — specifically pre/post-condition
specifications and loop invariants — can be combined with modern software engineering
tools (property-based testing via Hypothesis, runtime assertions) to build a verifiably
correct code generation system.

The pipeline is:

```
Algorithm Name
      │
      ▼
┌─────────────────┐    ┌─────────────────────┐
│  Code Generator │    │  Spec Generator      │
│  (code_gen.py)  │    │  (spec_gen.py)       │
│                 │    │  Pre / Post / Inv    │
└────────┬────────┘    └──────────┬───────────┘
         │                        │
         ▼                        ▼
┌─────────────────────────────────────────────┐
│               Verification Engine           │
│                                             │
│   ┌─────────────────┐  ┌─────────────────┐  │
│   │  Assertion Engine│  │  Property Tests │  │
│   │  (assertions.py) │  │  (tests.py)     │  │
│   │  Pre → Exec → Post│  │  Hypothesis PBT│  │
│   └─────────────────┘  └─────────────────┘  │
└────────────────────┬────────────────────────┘
                     │
                     ▼
              Streamlit UI (app.py)
              ✅ Pass / ❌ Fail Report
```

**Key insight:** code generation alone is not sufficient for safety-critical or
research-grade software. This system treats *specification* as a first-class artifact
and *verification* as a mandatory pipeline stage — not an afterthought.

---

## Architecture

### Layer 1: Generation (`generator/`)

| Module | Responsibility |
|--------|----------------|
| `code_gen.py` | Returns the Python source code string for any registered algorithm. Uses a decorator-based registry — adding a new algorithm requires only adding one `@register("Name")` function. |
| `spec_gen.py` | Returns a `FormalSpec` TypedDict for each algorithm: `pre`, `post`, `invariant`, `complexity`, `notes`. Decoupled from code so specs can be read statically. |

### Layer 2: Verification (`verifier/`)

| Module | Responsibility |
|--------|----------------|
| `assertions.py` | **Runtime assertion engine.** Validates preconditions before execution and postconditions after. Uses a dispatch table so adding new algorithms is trivial. Never raises — all failures are captured as structured `AssertionResult` objects. |
| `tests.py` | **Property-based test suites** using Hypothesis. For each algorithm, declares 3–5 universal properties (correctness, soundness, completeness, etc.) and 5–7 deterministic edge cases. Returns structured `TestSuiteReport` objects. |

### Layer 3: UI (`app.py`)

Streamlit single-page app. Five tabs:
1. **Generated Code** — syntax-highlighted source + demo execution
2. **Formal Specification** — pre/post/invariant/notes in colour-coded panels
3. **Assertion Engine** — per-check pass/fail with kind badges and detail
4. **Property Tests** — Hypothesis results with counterexample display
5. **Complexity** — formatted asymptotic table + comparative analysis

---

## File Structure

```
verified_ai_codegen/
│
├── app.py                     ← Streamlit application entry point
│
├── generator/
│   ├── __init__.py
│   ├── code_gen.py            ← Algorithm source code generator
│   └── spec_gen.py            ← Formal specification generator
│
├── verifier/
│   ├── __init__.py
│   ├── assertions.py          ← Runtime pre/post-condition checker
│   └── tests.py               ← Hypothesis property-based tests
│
├── examples/
│   ├── binary_search.json     ← Documented test cases + references
│   └── linear_search.json
│
├── requirements.txt
└── README.md
```

---

## What is Verification?

In software engineering, **verification** answers the question:

> *"Does the program do what its specification says it should do?"*

This is distinct from **validation** ("are we building the right thing?").

This project uses three increasingly rigorous techniques:

### 1. Runtime Assertions (Executable Specifications)
Preconditions and postconditions from the formal spec are translated into Python
`assert` statements that execute when the program runs. If the code violates the
spec, an `AssertionError` is raised immediately at the point of failure.

This is analogous to **Design by Contract** (Bertrand Meyer, 1988) and is the
foundation of tools like Eiffel, JML (Java), and Dafny.

### 2. Property-Based Testing (Hypothesis)
Instead of checking specific examples, we state **universal properties** and let
Hypothesis verify them over hundreds of randomly generated inputs:

```
∀ sorted arrays arr, ∀ integer target:
  binary_search(arr, target) ≠ -1  ⟹  arr[binary_search(arr, target)] == target
```

This is significantly stronger than unit testing because it:
- Covers input space systematically rather than at a programmer's discretion
- Automatically finds edge cases (empty lists, duplicates, large values)
- Provides **minimal counterexamples** when failures occur

### 3. Formal Specifications (Hoare Logic)
Specifications follow the **Hoare Triple** formalism:

```
{ P }  C  { Q }
```

- `P` (precondition): what must hold before `C` executes
- `C` (command): the algorithm
- `Q` (postcondition): what is guaranteed to hold after `C` completes

Combined with **loop invariants**, this provides a mathematical basis for
proving algorithm correctness — even without a mechanical proof assistant.

---

## Testing vs Verification

This is one of the most important distinctions in formal methods:

| Dimension | Testing | Verification |
|-----------|---------|--------------|
| **Goal** | Find bugs | Prove absence of bugs |
| **Coverage** | Finite set of inputs | All possible inputs (in scope) |
| **Result** | "No bug found in these N cases" | "Bug cannot exist" (for the proven property) |
| **Dijkstra quote** | *"Testing can show the presence of bugs, never their absence"* | Verification aims to show absence |
| **This project** | Property tests (Hypothesis) | Runtime assertions + formal specs |
| **Industrial tools** | pytest, JUnit | Dafny, Coq, TLA+, CBMC, Z3 |

**Important caveat:** Property-based testing, while much stronger than unit testing,
is still *testing* — not full formal verification. Hypothesis generates a large but
finite number of examples. True formal verification would require a mechanised proof
(e.g., using Dafny or Coq) that covers *all* possible inputs mathematically.

This project occupies the space **between** classical testing and full formal verification
— a pragmatic middle ground increasingly used in industry (e.g., AWS using TLA+ for
distributed systems, seL4 using Isabelle/HOL for OS kernels).

---

## Supported Algorithms

| Algorithm | Time Complexity | Key Precondition | Key Postcondition |
|-----------|-----------------|------------------|-------------------|
| Binary Search | O(log n) | Array must be sorted | Returns correct index or -1 |
| Linear Search | O(n) | None (works on any list) | Returns FIRST occurrence or -1 |
| Bubble Sort | O(n²) | None | Returns sorted permutation |
| Insertion Sort | O(n²) best O(n) | None | Returns sorted permutation |

---

## Installation & Running

### Prerequisites

- Python 3.10 or higher
- pip

### Setup

```bash
# 1. Clone / navigate to the project directory
cd verified_ai_codegen

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Streamlit app
streamlit run app.py
```

The app will open at `http://localhost:8501` in your browser.

### Dependencies (`requirements.txt`)
```
streamlit>=1.32.0
hypothesis>=6.100.0
```

---

## System Walkthrough

1. **Select an algorithm** from the sidebar dropdown.
2. The system **generates the source code** (generator/code_gen.py).
3. The system **generates the formal specification** (generator/spec_gen.py).
4. The **assertion engine** (verifier/assertions.py) validates a demo input:
   - Checks all preconditions
   - Executes the function
   - Checks all postconditions
5. The **Hypothesis test suite** (verifier/tests.py) runs:
   - Universal properties (100–150 random examples each)
   - Deterministic edge cases
6. Results are displayed in a **five-tab Streamlit interface**.

---

## Limitations

This system is an **educational and research demonstration**, not a production
formal verification tool. Known limitations:

1. **Not full formal verification.** Property-based testing checks a large but finite
   number of cases. A mathematical proof (e.g., in Dafny or Coq) is required to claim
   correctness for *all* possible inputs.

2. **Specifications are manually written.** In a true AI-assisted formal methods pipeline,
   specifications would be inferred or synthesised from the code. Here they are hand-coded.

3. **Limited algorithm set.** Only four algorithms are currently implemented. The
   decorator-based registry makes adding more trivial, but this has not been done.

4. **No SMT/SAT solver integration.** A more rigorous system would use Z3 or CVC5 to
   discharge proof obligations rather than executing assertions at runtime.

5. **No type-level verification.** Python's dynamic typing means type errors are caught
   at runtime, not statically. A language like Haskell (with dependent types) or F* would
   allow type-level correctness proofs.

6. **Hypothesis databases not persisted.** Each run starts fresh. In production, Hypothesis
   stores discovered counterexamples in a database to prevent regressions.

7. **Concurrent execution not considered.** Specifications assume sequential single-threaded
   execution. Race conditions and atomicity are outside scope.

---

## Future Improvements

### Near-term (low complexity)
- Add more algorithms: Merge Sort, Quick Sort, BFS, DFS, Dijkstra
- Persist Hypothesis database between runs
- Add a "manual input" panel to test user-supplied inputs
- Export verification reports as PDF/JSON

### Medium-term (moderate complexity)
- **Integrate Z3 (SMT solver):** Translate pre/post-conditions into Z3 formulae and
  attempt automated proof discharge. Failures would be genuine formal counterexamples.
- **Dafny code generation:** Generate Dafny (a formally verified language) alongside
  Python, enabling machine-checked proofs.
- **Mutation testing:** Introduce deliberate bugs into the code and verify that the
  property suite catches them (measures test suite adequacy).

### Long-term (research-grade)
- **Specification inference:** Use LLMs to suggest pre/post-conditions from code, then
  verify them with an SMT solver — closing the AI + formal methods loop.
- **Proof synthesis:** Use neural-guided proof search (e.g., CoqGym, LEAN 4 + Mathlib)
  to attempt automated formal proofs.
- **Runtime verification for concurrent systems:** Extend to monitor distributed
  algorithms using temporal logic (LTL/CTL) properties.

---

## References

1. Hoare, C.A.R. (1969). *An axiomatic basis for computer programming.*
   Communications of the ACM, 12(10), 576–580.

2. Meyer, B. (1988). *Object-Oriented Software Construction.* Prentice Hall.
   (Introduces Design by Contract)

3. MacIver, D. et al. (2019). *Hypothesis: A new approach to property-based testing.*
   Journal of Open Source Software, 4(43), 1891.

4. Knuth, D.E. (1998). *The Art of Computer Programming, Volume 3: Sorting and
   Searching* (2nd ed.). Addison-Wesley.

5. Leino, K.R.M. (2010). *Dafny: An automatic program verifier for functional
   correctness.* LNCS 6355, 348–370.

6. de Moura, L., & Bjørner, N. (2008). *Z3: An efficient SMT solver.*
   TACAS 2008, LNCS 4963, 337–340.

---

*Built as a research demonstration for program verification concepts.*
*Language: Python 3.10+ · UI: Streamlit · Testing: Hypothesis*
