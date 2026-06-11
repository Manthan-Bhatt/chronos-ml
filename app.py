import streamlit as st
import pandas as pd
from db import query

st.set_page_config(
    page_title="Chronos ML",
    page_icon="⏱",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
  .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
  [data-testid="metric-container"] {
    background: #F7F7F5;
    border: 0.5px solid #E0DED6;
    border-radius: 10px;
    padding: 14px 18px;
  }
  [data-testid="stSidebar"] {
    border-right: 0.5px solid #E0DED6;
  }
  [data-testid="stDataFrame"] {
    border: 0.5px solid #E0DED6;
    border-radius: 8px;
    overflow: hidden;
  }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────
st.title("⏱ Chronos ML")
st.caption("AI Model Versioning & Experiment Tracking")
st.divider()

# ── Stat cards ────────────────────────────────────────────
counts = query("""
    SELECT
      (SELECT COUNT(*) FROM model)        AS models,
      (SELECT COUNT(*) FROM training_run) AS runs,
      (SELECT COUNT(*) FROM deployment)   AS deployments,
      (SELECT COUNT(*) FROM dataset)      AS datasets
""")[0]

running = query("""
    SELECT COUNT(*) AS c FROM training_run WHERE status = 'Running'
""")[0]["c"]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Models",        counts["models"])
col2.metric("Training Runs", counts["runs"], delta=f"{running} running")
col3.metric("Deployments",   counts["deployments"])
col4.metric("Datasets",      counts["datasets"])

st.divider()

# ── Recent runs ───────────────────────────────────────────
st.subheader("Recent Training Runs")

runs = query("""
    SELECT
        r.run_id,
        m.model_name,
        mv.algorithm,
        r.status,
        r.start_time,
        r.end_time
    FROM training_run r
    JOIN model m ON r.model_id = m.model_id
    JOIN model_version mv
      ON r.model_id = mv.model_id
     AND r.version_no = mv.version_no
    ORDER BY r.created_at DESC
    LIMIT 10
""")

if runs:
    df = pd.DataFrame(runs)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "run_id":     st.column_config.TextColumn("Run ID"),
            "model_name": st.column_config.TextColumn("Model"),
            "algorithm":  st.column_config.TextColumn("Algorithm"),
            "status":     st.column_config.TextColumn("Status"),
            "start_time": st.column_config.DatetimeColumn("Started",  format="MMM D, h:mm a"),
            "end_time":   st.column_config.DatetimeColumn("Finished", format="MMM D, h:mm a"),
        }
    )
else:
    st.info("No training runs yet.")

st.divider()

# ── Models + Deployments side by side ─────────────────────
left, right = st.columns(2)

with left:
    st.subheader("Models")
    models = query("""
        SELECT model_name, problem_type, category,
               is_public, created_at
        FROM model
        ORDER BY created_at DESC
        LIMIT 8
    """)
    if models:
        st.dataframe(
            pd.DataFrame(models),
            use_container_width=True,
            hide_index=True,
            column_config={
                "model_name":   st.column_config.TextColumn("Name"),
                "problem_type": st.column_config.TextColumn("Type"),
                "category":     st.column_config.TextColumn("Category"),
                "is_public":    st.column_config.CheckboxColumn("Public"),
                "created_at":   st.column_config.DatetimeColumn("Created", format="MMM D YYYY"),
            }
        )
    else:
        st.info("No models yet.")

with right:
    st.subheader("Deployments")
    deployments = query("""
        SELECT d.deployment_id,
               m.model_name,
               d.version_number,
               d.environment,
               d.status,
               d.deployed_at
        FROM deployment d
        JOIN model m ON d.model_id = m.model_id
        ORDER BY d.deployed_at DESC
        LIMIT 8
    """)
    if deployments:
        st.dataframe(
            pd.DataFrame(deployments),
            use_container_width=True,
            hide_index=True,
            column_config={
                "deployment_id": st.column_config.TextColumn("ID"),
                "model_name":    st.column_config.TextColumn("Model"),
                "version_number":st.column_config.TextColumn("Version"),
                "environment":   st.column_config.TextColumn("Env"),
                "status":        st.column_config.TextColumn("Status"),
                "deployed_at":   st.column_config.DatetimeColumn("Deployed", format="MMM D YYYY"),
            }
        )
    else:
        st.info("No deployments yet.")