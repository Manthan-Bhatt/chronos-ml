import streamlit as st
import pandas as pd
from db import query

st.set_page_config(page_title="Deployments", page_icon="🚀", layout="wide")

st.title("🚀 Deployments")
st.divider()

# ── Status summary ────────────────────────────────────────
statuses = query("""
    SELECT status, COUNT(*) AS count
    FROM deployment
    GROUP BY status
    ORDER BY count DESC
""")

cols = st.columns(len(statuses))
for i, row in enumerate(statuses):
    cols[i].metric(row["status"], row["count"])

st.divider()

# ── Filter by environment ─────────────────────────────────
envs = ["All"] + [r["environment"] for r in query("SELECT DISTINCT environment FROM deployment ORDER BY environment")]
selected_env = st.selectbox("Filter by Environment", envs)

where  = "" if selected_env == "All" else "WHERE d.environment = %s"
params = [] if selected_env == "All" else [selected_env]

deployments = query(f"""
    SELECT d.deployment_id, m.model_name, d.version_number,
           d.environment, d.status, d.deployed_at, d.retired_at
    FROM deployment d
    JOIN model m ON d.model_id = m.model_id
    {where}
    ORDER BY d.deployed_at DESC
""", params or None)

st.subheader(f"All Deployments ({len(deployments)})")

if deployments:
    st.dataframe(
        pd.DataFrame(deployments),
        use_container_width=True,
        hide_index=True,
        column_config={
            "deployment_id":  st.column_config.TextColumn("ID"),
            "model_name":     st.column_config.TextColumn("Model"),
            "version_number": st.column_config.TextColumn("Version", width="small"),
            "environment":    st.column_config.TextColumn("Environment"),
            "status":         st.column_config.TextColumn("Status"),
            "deployed_at":    st.column_config.DatetimeColumn("Deployed", format="MMM D YYYY"),
            "retired_at":     st.column_config.DatetimeColumn("Retired",  format="MMM D YYYY"),
        }
    )
else:
    st.info("No deployments found.")