import streamlit as st
import subprocess
import os
from datetime import datetime

st.set_page_config(page_title="Quality Dashboard", layout="wide")
st.title("📊 Quality Dashboard")
st.caption(f"Realtime Disasters Monitoring • Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.sidebar.success("✅ Connected to qa-cicd-framework")

# Debug folders
st.subheader("🔍 Debug: Folders in this app")
st.write(os.listdir("."))

@st.cache_data(ttl=300)
def run_checks():
    data = {"lint_issues": 0, "tests_passed": 0, "tests_failed": 0}

    try:
        result = subprocess.run(["ruff", "check", "."], capture_output=True, text=True)
        data["lint_issues"] = result.stdout.count("E") + result.stdout.count("F") + result.stdout.count("W")
        st.subheader("📋 Ruff Linting Results")
        st.code(result.stdout, language="bash")
    except Exception as e:
        st.error(f"Ruff error: {e}")

    # Tests
    try:
        result = subprocess.run(["pytest", "tests/unit", "--tb=no", "--quiet"], capture_output=True, text=True)
        data["tests_passed"] = result.stdout.count("passed")
        data["tests_failed"] = result.stdout.count("failed")
    except:
        st.info("No tests/ folder found yet → Tests will appear once you add them.")

    return data

metrics = run_checks()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Lint Issues", metrics["lint_issues"])
with col2:
    st.metric("Tests Passed", metrics["tests_passed"])
with col3:
    st.metric("Tests Failed", metrics["tests_failed"])

st.caption("Quality Dashboard • Powered by qa-cicd-framework")
