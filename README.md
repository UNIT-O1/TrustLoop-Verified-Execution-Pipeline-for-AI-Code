# 🔬 Verified AI Code Generation (VACG)

> **Don’t trust AI-generated code — verify it.**

AI can generate code that looks correct but fails silently on edge cases, violates assumptions (like unsorted inputs), or lacks any formal correctness guarantees. In critical systems, this isn't just a bug—it’s a liability.

The 1996 Ariane 5 Flight 501 failure—although ultimately a human design and verification error—happened because logic wasn’t properly validated, not because the code couldn’t be written. In a near future where AI will dominate code generation, this exact class of failure becomes even more dangerous. This project turns AI code generation from a guess into a proof.

---

## 🚨 The Problem

Traditional "Generate → Run" workflows are dangerous for critical logic because:

- **Silent Failures:** AI code often works for common cases but breaks on "unlikely" edge cases  
- **Implicit Assumptions:** Code may assume a sorted list or positive integers without checking  
- **No Mathematical Grounding:** Unit tests only prove the code works for the inputs you thought of  

---

## 💡 The VACG Pipeline

We shift the paradigm from **Generate → Run** to:
Generate ➔ Specify ➔ Verify ➔ Execute


Code must pass multiple layers of correctness checks before it is ever accepted for execution.

---

## 1. Specification Layer (The Contract)

Each algorithm is paired with a **Formal Specification**:

- **Preconditions:** What must be true before execution (e.g., `arr` is sorted)  
- **Postconditions:** What must be guaranteed after execution (e.g., `result` is correct)  
- **Invariants:** What must remain true during execution  

---

## ⚙️ Three Layers of Defense

### 🔹 Layer A: Runtime Assertions (Design by Contract)

- Enforces preconditions before execution  
- Validates postconditions after execution  
- Stops execution immediately on violation  

---

### 🔹 Layer B: Property-Based Testing (Hypothesis)

- Define **properties**, not test cases  
- Automatically generates hundreds of random inputs  
- Finds edge cases and unexpected failures  

---

### 🔹 Layer C: Formal Verification with Z3 (The Proof)

This is the core of the system.

| Approach | What it does | Reliability |
|----------|-------------|------------|
| Unit Testing | Tests specific inputs | 🔴 Low |
| Property Testing | Tests many inputs | 🟡 Medium |
| Z3 Solver | Proves for all inputs | 🟢 Absolute |

---

### 🧠 How Z3 Works (Intuition)

You don’t give Z3 values — you give it logic.

- Instead of: *“If x = 5, does it work?”*  
- Z3 asks: *“Is there ANY value of x that breaks this?”*

If a counterexample exists → bug found  
If none exists → property is mathematically proven (within the model)

---

## 🔍 Verification Examples

### 🚀 Safe Integer Conversion (Ariane 5 Case Study)

- Constraint: `x ∈ [-32768, 32767]`  
- Z3 checks if any value violates this  
- Prevents overflow failures before execution  

---

### 🔎 Binary Search & Sorting

- **Sorting:** Ensures output is ordered and no elements are lost  
- **Binary Search:** Guarantees valid indexing and correct convergence  

---

### 🔢 Prime Check (Bug Demo)

A deliberately flawed implementation is included.

- Incorrect bound (`n/3`)  
- Z3 finds counterexample (e.g., `n = 9`)  
- Demonstrates real bug detection via formal reasoning  

---

## 🚀 Run the Project

1. Clone the repository  
2. Install dependencies:

```bash
pip install -r requirements.txt

https://www.youtube.com/watch?v=N6PWATvLQCY
This video demonstrates the Ariane 5 Flight 501 disaster and highlights the real-world impact of unverified software logic
