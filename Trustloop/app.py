import sys
import os
import time
from typing import Any
import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from generator.code_gen import generate_code, get_supported_algorithms
from generator.spec_gen import get_spec
from verifier.assertions import run_assertions
from verifier.tests import run_tests
from verifier.formal import (
    verify_prime_logic,
    verify_sort_invariant,
    verify_boolean_and_logic,
    verify_factorial_bounds,
    verify_gcd_logic,
    verify_ariane_safety,
)

st.set_page_config(page_title="Verified AI Code Gen", page_icon="🔬", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main-title { font-family: 'Playfair Display', serif; font-size: 2.4rem; font-weight: 600; color: #0f172a; margin-bottom: 0.25rem; }
.main-subtitle { font-size: 1rem; color: #64748b; margin-bottom: 2rem; font-weight: 300; letter-spacing: 0.02em; }
.metric-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.1rem 1.4rem; text-align: center; }
.metric-value { font-size: 2.2rem; font-weight: 700; line-height: 1; }
.metric-label { font-size: 0.78rem; color: #64748b; margin-top: 0.3rem; text-transform: uppercase; letter-spacing: 0.08em; }
.metric-pass  { color: #16a34a; }
.metric-fail  { color: #dc2626; }
.metric-total { color: #2563eb; }
.spec-box { background: #fefce8; border-left: 4px solid #ca8a04; border-radius: 0 8px 8px 0; padding: 1rem 1.2rem; margin-bottom: 1rem; font-size: 0.92rem; line-height: 1.65; white-space: pre-wrap; font-family: 'Inter', sans-serif; }
.spec-box-blue { background: #eff6ff; border-left: 4px solid #3b82f6; border-radius: 0 8px 8px 0; padding: 1rem 1.2rem; margin-bottom: 1rem; font-size: 0.92rem; line-height: 1.65; white-space: pre-wrap; }
.spec-box-green { background: #f0fdf4; border-left: 4px solid #16a34a; border-radius: 0 8px 8px 0; padding: 1rem 1.2rem; margin-bottom: 1rem; font-size: 0.92rem; line-height: 1.65; white-space: pre-wrap; }
.spec-box-purple { background: #faf5ff; border-left: 4px solid #9333ea; border-radius: 0 8px 8px 0; padding: 1rem 1.2rem; margin-bottom: 1rem; font-size: 0.92rem; line-height: 1.65; white-space: pre-wrap; }
.assert-row { display: flex; align-items: flex-start; gap: 0.6rem; padding: 0.55rem 0.8rem; border-radius: 8px; margin-bottom: 0.4rem; font-size: 0.88rem; line-height: 1.45; }
.assert-pass { background: #f0fdf4; border: 1px solid #bbf7d0; }
.assert-fail { background: #fef2f2; border: 1px solid #fecaca; }
.assert-icon { font-size: 1rem; flex-shrink: 0; margin-top: 1px; }
.assert-name { font-weight: 600; color: #1e293b; }
.assert-detail { color: #64748b; font-size: 0.82rem; margin-top: 0.2rem; }
.assert-error  { color: #dc2626; font-size: 0.82rem; margin-top: 0.2rem; font-family: 'JetBrains Mono', monospace; }
.assert-kind-badge { background: #e2e8f0; color: #475569; border-radius: 4px; padding: 0.05rem 0.4rem; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; flex-shrink: 0; align-self: center; }
.verdict-pass { background: linear-gradient(135deg, #16a34a, #15803d); color: white; border-radius: 12px; padding: 1.2rem 1.8rem; text-align: center; font-size: 1.3rem; font-weight: 700; letter-spacing: 0.03em; margin-bottom: 1.5rem; }
.verdict-fail { background: linear-gradient(135deg, #dc2626, #b91c1c); color: white; border-radius: 12px; padding: 1.2rem 1.8rem; text-align: center; font-size: 1.3rem; font-weight: 700; letter-spacing: 0.03em; margin-bottom: 1.5rem; }
.section-header { font-size: 1.05rem; font-weight: 700; color: #0f172a; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.4rem; }
</style>
""", unsafe_allow_html=True)

def load_function(code: str, fn_name: str):
    namespace: dict[str, Any] = {}
    exec(compile(code, "<generated>", "exec"), namespace)
    return namespace[fn_name]

ALGO_FN_NAMES = {
    "Binary Search":  "binary_search",
    "Linear Search":  "linear_search",
    "Bubble Sort":    "bubble_sort",
    "Insertion Sort": "insertion_sort",
    "Prime Check (Buggy)": "is_prime_buggy",
    "Boolean AND": "boolean_and",
    "Factorial": "factorial",
    "GCD (Recursive)": "gcd",
    "Ariane 5 Safe Float-to-Int": "safe_convert_64_to_16",
}

DEMO_INPUTS = {
    "Binary Search":  {"arr": [1, 3, 5, 7, 9, 11, 15, 20, 25, 30], "target": 11},
    "Linear Search":  {"arr": [64, 34, 25, 12, 22, 11, 90], "target": 22},
    "Bubble Sort":    {"arr": [64, 34, 25, 12, 22, 11, 90]},
    "Insertion Sort": {"arr": [64, 34, 25, 12, 22, 11, 90]},
    "Prime Check (Buggy)": {"n": 4},
    "Boolean AND": {"a": True, "b": False},
    "Factorial": {"n": 5},
    "GCD (Recursive)": {"a": 48, "b": 18},
    "Ariane 5 Safe Float-to-Int": {"val": 45000.5}, # This will trigger the safe error
}

def run_z3_verification(algorithm: str):
    if algorithm == "Prime Check (Buggy)":
        return verify_prime_logic()
    if "Sort" in algorithm:
        return verify_sort_invariant(algorithm)
    if algorithm == "Boolean AND":
        return verify_boolean_and_logic()
    if algorithm == "Factorial":
        return verify_factorial_bounds()
    if algorithm == "GCD (Recursive)":
        return verify_gcd_logic()
    if algorithm == "Ariane 5 Safe Float-to-Int":
        return verify_ariane_safety()
    return (False, "No formal proof defined for this algorithm.")

def render_assertion_row(a) -> str:
    icon  = "✅" if a.passed else "❌"
    cls   = "assert-pass" if a.passed else "assert-fail"
    error = f'<div class="assert-error">↳ {a.error}</div>' if a.error else ""
    detail = f'<div class="assert-detail">{a.detail}</div>' if a.detail else ""
    return f'<div class="assert-row {cls}"><span class="assert-icon">{icon}</span><div style="flex:1"><span class="assert-name">{a.name}</span><span class="assert-kind-badge" style="margin-left:0.5rem">{a.kind}</span>{detail}{error}</div></div>'

def render_test_row(t) -> str:
    icon = "✅" if t.passed else "❌"
    cls  = "assert-pass" if t.passed else "assert-fail"
    ce   = f'<div class="assert-error">Counterexample: {t.counterexample}</div>' if t.counterexample else ""
    examples = f'<div class="assert-detail">Hypothesis examples: {t.num_examples}</div>' if t.num_examples else ""
    return f'<div class="assert-row {cls}"><span class="assert-icon">{icon}</span><div style="flex:1"><span class="assert-name">{t.name}</span><span class="assert-kind-badge" style="margin-left:0.5rem">{t.kind}</span><div class="assert-detail">{t.detail}</div>{examples}{ce}</div></div>'

with st.sidebar:
    st.markdown("## 🔬 Algorithm Selector")
    algos = get_supported_algorithms()
    selected = st.selectbox("Choose an algorithm:", algos, index=0)

st.markdown('<div class="main-title">🔬 Verified AI-Assisted Code Generation</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">Formal Specifications · Runtime Assertions · Property-Based Testing · Z3 Proofs</div>', unsafe_allow_html=True)

code_src = generate_code(selected)
spec     = get_spec(selected)
fn_name  = ALGO_FN_NAMES[selected]
fn       = load_function(code_src, fn_name)

with st.spinner("Running verification engine …"):
    t0 = time.time()
    demo_inputs = DEMO_INPUTS[selected]
    assert_report = run_assertions(selected, fn, demo_inputs)
    test_report   = run_tests(selected, fn)
    
    z3_passed, z3_msg = run_z3_verification(selected)
    elapsed = time.time() - t0

all_ok = assert_report.all_passed and test_report.all_passed and z3_passed
total_checks = len(assert_report.assertions) + len(test_report.results) + 1
passed_checks = assert_report.pass_count + test_report.pass_count + (1 if z3_passed else 0)
failed_checks = assert_report.fail_count + test_report.fail_count + (0 if z3_passed else 1)

if all_ok:
    st.markdown(f'<div class="verdict-pass">✅ VERIFICATION PASSED — {passed_checks}/{total_checks} checks passed &nbsp;|&nbsp; {elapsed:.2f}s</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="verdict-fail">❌ VERIFICATION FAILED — {failed_checks} check(s) failed &nbsp;|&nbsp; {elapsed:.2f}s</div>', unsafe_allow_html=True)

tab_code, tab_spec, tab_assert, tab_tests, tab_z3 = st.tabs([
    "📄 Code", "📐 Spec", "🔒 Assertions", "🧪 Tests", "🛡️ Z3 Formal Proof"
])

with tab_code:
    st.markdown(f'<div class="section-header">📄 Generated Implementation: {selected}</div>', unsafe_allow_html=True)
    st.code(code_src, language="python")
    st.markdown('<div class="section-header">▶ Demo Execution</div>', unsafe_allow_html=True)
    input_str = ", ".join(f"{k}={v!r}" for k, v in demo_inputs.items())
    st.markdown(f"**Input:** `{fn_name}({input_str})`")
    if assert_report.output is not None:
        st.markdown(f"**Output:** `{assert_report.output!r}`")
    else:
        st.error("Execution did not complete.")

with tab_spec:
    st.markdown(f'<div class="section-header">📐 Formal Specification: {selected}</div>', unsafe_allow_html=True)
    st.markdown("#### 🔴 Precondition `P`")
    st.markdown(f'<div class="spec-box">{spec["pre"]}</div>', unsafe_allow_html=True)
    st.markdown("#### 🟢 Postcondition `Q`")
    st.markdown(f'<div class="spec-box-green">{spec["post"]}</div>', unsafe_allow_html=True)
    st.markdown("#### 🔵 Loop / Structural Invariant")
    st.markdown(f'<div class="spec-box-blue">{spec["invariant"]}</div>', unsafe_allow_html=True)
    st.markdown("#### 🟣 Design Notes")
    st.markdown(f'<div class="spec-box-purple">{spec["notes"]}</div>', unsafe_allow_html=True)

with tab_assert:
    st.markdown(f'<div class="section-header">🔒 Runtime Assertion Report: {selected}</div>', unsafe_allow_html=True)
    for a in assert_report.assertions:
        st.markdown(render_assertion_row(a), unsafe_allow_html=True)

with tab_tests:
    st.markdown(f'<div class="section-header">🧪 Property-Based Test Report: {selected}</div>', unsafe_allow_html=True)
    for t in test_report.results:
        st.markdown(render_test_row(t), unsafe_allow_html=True)

with tab_z3:
    st.markdown('<div class="section-header">🛡️ Z3 SMT Solver Verification</div>', unsafe_allow_html=True)
    
    z3_res, z3_m = run_z3_verification(selected)

    # Render Results
    if z3_res:
        st.success(f"✅ {z3_m}")
    else:
        st.error(f"❌ Formal Verification Failed/Not Applicable")
        st.markdown(f"**Result:** {z3_m}")
        if selected == "Ariane 5 Safe Float-to-Int":
            st.info("Historically, the Ariane 5 failed because this proof was never run on the 64-bit conversion logic.")