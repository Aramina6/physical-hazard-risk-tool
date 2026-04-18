import streamlit as st
import subprocess
import os
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Quality Dashboard", layout="wide")
st.title("📊 Quality Dashboard")
st.caption(f"Realtime Disasters Monitoring • Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.sidebar.success("✅ Connected to qa-cicd-framework")

# ====================== DEBUG: Show what folders actually exist ======================
st.subheader("🔍 Debug: Folders in this app")
st.write(os.listdir("."))

# ====================== Run checks ======================
@st.cache_data(ttl=300)
def run_checks():
    data = {"lint_issues": 0, "tests_passed": 0, "tests_failed": 0}

    # Try possible submodule folder names
    possible_paths = ["qa-framework", "qa-cicd-framework", "."]
    qa_path = None

    for path in possible_paths:
        if os.path.exists(path):
            qa_path = path
            break

    if qa_path:
        st.success(f"✅ Found QA folder: **{qa_path}**")
    else:
        st.error("❌ Could not find qa-framework or qa-cicd-framework folder")

    # Linting
    try:
        result = subprocess.run(["ruff", "check", qa_path or "."], capture_output=True, text=True)
        data["lint_issues"] = result.stdout.count("E") + result.stdout.count("F") + result.stdout.count("W")
        st.code(result.stdout, language="bash")
    except Exception as e:
        st.error(f"Ruff error: {e}")

    # Tests
    try:
        test_path = f"{qa_path}/tests/unit" if qa_path and qa_path != "." else "tests/unit"
        result = subprocess.run(["pytest", test_path, "--tb=no", "--quiet"], capture_output=True, text=True)
        data["tests_passed"] = result.stdout.count("passed")
        data["tests_failed"] = result.stdout.count("failed")
    except:
        pass

    return data

metrics = run_checks()

# Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Lint Issues", metrics["lint_issues"])
with col2:
    st.metric("Tests Passed", metrics["tests_passed"])
with col3:
    st.metric("Tests Failed", metrics["tests_failed"])

st.caption("Quality Dashboard • Connected to qa-cicd-framework")
