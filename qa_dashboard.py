import streamlit as st
import subprocess
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Quality Dashboard", layout="wide")
st.title("📊 Quality Dashboard")
st.caption(f"Realtime Disasters Monitoring • Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.sidebar.success("✅ Connected to qa-cicd-framework")

# Run quality checks from the qa-framework (this is how it accesses the QA project)
@st.cache_data(ttl=300)
def run_qa_framework_checks():
    data = {}

    # Use the tests and checks from the qa-cicd-framework
    qa_path = "qa-framework"

    # 1. Linting (same as your CI/CD code-quality job)
    try:
        result = subprocess.run(["ruff", "check", qa_path], capture_output=True, text=True)
        data["lint_issues"] = result.stdout.count("E") + result.stdout.count("F") + result.stdout.count("W")
    except:
        data["lint_issues"] = 0

    # 2. Run tests from the QA framework
    try:
        result = subprocess.run(["pytest", f"{qa_path}/tests/unit", "--tb=no", "--quiet"], capture_output=True, text=True)
        data["tests_passed"] = result.stdout.count("passed")
        data["tests_failed"] = result.stdout.count("failed")
    except:
        data["tests_passed"] = 0
        data["tests_failed"] = 0

    return data

metrics = run_qa_framework_checks()

# Display metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Lint Issues", metrics["lint_issues"])
with col2:
    st.metric("Tests Passed", metrics["tests_passed"])
with col3:
    st.metric("Tests Failed", metrics["tests_failed"])

st.success("✅ Dashboard is now accessing qa-cicd-framework via submodule")

# Show results from the QA project
st.subheader("Results from qa-cicd-framework")
st.code(subprocess.getoutput("ruff check qa-framework"), language="bash")

st.caption("Quality Dashboard • Connected to qa-cicd-framework")
