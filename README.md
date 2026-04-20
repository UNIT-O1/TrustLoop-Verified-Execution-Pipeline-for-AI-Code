# TrustLoop-Verified-Execution-Pipeline-for-AI-Code

### *From AI Output to Provable Correctness*

> **AI can generate code. This system proves whether it deserves to be trusted.**

## 🚨 The Core Problem

AI-generated code is accelerating development—but it introduces a critical risk:

> ❗ **There is no inherent guarantee that AI-generated code is correct.**

Even when it “looks right,” it can fail due to:

* Hidden logical errors
* Edge-case failures
* Invalid assumptions
* Unsafe operations

In safety-critical systems (aerospace, finance, infrastructure), this is unacceptable.

---

## 💡 What This Project Actually Solves

This project does **one thing extremely well**:

> ✅ **It verifies the correctness of AI-generated code with strong guarantees.**

It does **NOT** attempt to:

* Train LLMs
* Improve code generation quality
* Replace existing AI models

Instead, it focuses on the missing layer:

> 🧠 **Trust**

---

## ⚠️ Important Scope Clarification (Read This First)

### 🚧 No Live LLM in the Pipeline

This system **does NOT generate code at runtime using an LLM**.

> ❗ All code used in the pipeline is **pre-generated and stored**.

---

### 🎯 Why This Is a Strength (Not a Limitation)

This is a **deliberate research decision**, not a missing feature.

#### 1️⃣ Pure Focus on Verification

We isolate the real problem:

> “Can we *prove* code correctness?”

Not:

> “Can we generate code?”

This ensures:

* Zero noise from LLM randomness
* Full focus on correctness guarantees

---

#### 2️⃣ Deterministic & Reproducible Results

Unlike live AI systems:

* No API variability
* No version drift
* No stochastic outputs

> Same input → same verification result (always)

This makes the system:

* Research-grade
* Benchmarkable
* Scientifically valid

---

#### 3️⃣ Stronger Validation of the Verification Engine

The pipeline works on:

* Arbitrary pre-generated code
* Including intentionally buggy implementations

Which proves:

> ✔️ Verification is **independent of the generator**

---

### 🔄 Future Direction (Planned, Not Implemented)

The architecture is designed to plug into:

* OpenAI
* Anthropic
* Google DeepMind

Future pipeline:

```text
LLM → Code + Spec → Verification → Feedback → Regeneration
```

---

## 🏗️ System Architecture

```text
Pre-Generated Code + Formal Spec
                ↓
      Verification Pipeline
                ↓
    PASS / FAIL + Diagnostics
                ↓
        Streamlit UI
```

---

## 🔍 The Three-Layer Verification Pipeline

This system does not rely on a single method.
It uses **three independent correctness guarantees**.

---

### 1️⃣ Runtime Assertions — *Design by Contract*

**What it does:**

* Enforces preconditions and postconditions during execution

**Example:**

* Binary Search requires sorted input
* Output must be valid index or -1

**Why it matters:**

* Prevents invalid execution states
* Catches violations immediately

> 🔒 Ensures the program behaves correctly for a given run

---

### 2️⃣ Property-Based Testing — *Hypothesis*

**What it does:**

* Tests universal properties across hundreds of random inputs

**Example property:**

```python
forall arr: sort(arr) == sorted(arr)
```

**Why it matters:**

* Discovers edge cases humans miss:

  * Empty arrays
  * Duplicates
  * Negative values

> 🧪 Demonstrates robustness across input space

---

### 3️⃣ Formal Verification — *Z3 SMT Solver*

**What it does:**

* Uses symbolic logic to prove correctness mathematically

**Capabilities:**

* Validates invariants
* Detects logical inconsistencies
* Proves correctness for *all possible inputs*

**Example:**

* Euclidean GCD correctness
* Loop invariant preservation

> 🧠 This is the strongest guarantee: **proof, not evidence**

---

## 📦 Module-Level Breakdown

---

### 🔹 `app.py` — Orchestrator

* Central execution engine
* Dynamically loads code using `exec()`
* Runs:

  * Assertions
  * Property tests
  * Formal proofs
* Outputs final verdict:

  * ✅ VERIFIED
  * ❌ FAILED

Tracks:

* Execution time
* Failure counts
* Pass/fail per layer

---

### 🔹 `generator/code_gen.py`

* Registry-based architecture (`@register`)
* Stores pre-generated implementations

Includes:

* Binary Search
* Sorting Algorithms
* GCD
* Factorial
* Safety-critical modules

---

### 🔹 `generator/spec_gen.py`

Defines formal specifications:

```python
FormalSpec = {
  "pre": condition_before_execution,
  "post": expected_outcome,
  "invariant": loop_property,
  "complexity": time_complexity
}
```

> 🔑 Separation of code and specification enables independent verification

---

### 🔹 `verifier/assertions.py`

* Implements **Hoare Logic**
* Validates:

  * Preconditions
  * Postconditions

Returns structured results with failure reasons

---

### 🔹 `verifier/tests.py`

* Uses Hypothesis
* Generates randomized test inputs
* Outputs:

  * Pass rate
  * Counterexamples

---

### 🔹 `verifier/formal.py`

* Integrates Z3 Solver
* Converts logic into symbolic constraints
* Proves:

  * Invariants
  * Mathematical correctness

---

## 🧪 Algorithms Included (and Why)

---

### 🔍 Binary Search

* Demonstrates strict preconditions
* Validates loop invariants

---

### 🔢 Sorting Algorithms

* Ideal for property-based testing
* Strong invariant reasoning

---

### 🔁 GCD (Euclidean Algorithm)

* Recursive correctness proof
* Mathematical validation

---

### 🔣 Factorial

* Base case + recursion correctness
* Inductive reasoning validation

---

### 🛡️ Safety-Critical Logic

Inspired by the **Ariane 5 Flight 501 failure**

Problem:

* Unsafe float → integer conversion caused overflow

Solution:

* Formally verify bounds:

  * Output ∈ [-32768, 32767]

> Demonstrates real-world impact of formal verification

---

## 📊 Why This Approach Matters

### Without Verification

* Code may appear correct
* Bugs remain hidden
* No guarantees

---

### With This System

* Multi-layer validation
* Mathematical guarantees
* Deterministic results

---

## 🚀 Getting Started

```bash
git clone https://github.com/your-repo/verified_ai_codegen
cd verified_ai_codegen
pip install -r requirements.txt
streamlit run app.py
```

---

## 📁 Project Structure

```text
verified_ai_codegen/
├── app.py
├── generator/
│   ├── code_gen.py
│   └── spec_gen.py
├── verifier/
│   ├── assertions.py
│   ├── tests.py
│   └── formal.py
├── requirements.txt
└── README.md
```

---

## 🔮 Future Work

* Live LLM integration
* Self-correcting agent loop
* CI/CD verification pipelines
* Large-scale formal proofs

---

## 🧠 Final Statement

> This project does not try to make AI generate better code.
>
> It ensures that **any generated code—good or bad—can be rigorously verified.**

