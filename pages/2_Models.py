import streamlit as st
import pandas as pd
from db import query

st.set_page_config(page_title="Models", page_icon="🧠", layout="wide")

st.title("🧠 Models")
st.divider()

# ── Filters ───────────────────────────────────────────────
col1, col2 = st.columns(2)
problem_types = ["All"] + [r["problem_type"] for r in query("SELECT DISTINCT problem_type FROM model ORDER BY problem_type")]
categories    = ["All"] + [r["category"]     for r in query("SELECT DISTINCT category FROM model ORDER BY category")]

selected_type = col1.selectbox("Problem Type", problem_types)
selected_cat  = col2.selectbox("Category", categories)

# ── Models table ──────────────────────────────────────────
where  = []
params = []
if selected_type != "All":
    where.append("problem_type = %s"); params.append(selected_type)
if selected_cat != "All":
    where.append("category = %s"); params.append(selected_cat)

where_clause = ("WHERE " + " AND ".join(where)) if where else ""

models = query(f"""
    SELECT model_id, model_name, problem_type, category,
           license_type, is_public, created_at
    FROM model
    {where_clause}
    ORDER BY created_at DESC
""", params or None)

st.subheader(f"All Models ({len(models)})")

if models:
    st.dataframe(
        pd.DataFrame(models),
        use_container_width=True,
        hide_index=True,
        column_config={
            "model_id":     st.column_config.TextColumn("ID"),
            "model_name":   st.column_config.TextColumn("Name"),
            "problem_type": st.column_config.TextColumn("Problem Type"),
            "category":     st.column_config.TextColumn("Category"),
            "license_type": st.column_config.TextColumn("License"),
            "is_public":    st.column_config.CheckboxColumn("Public"),
            "created_at":   st.column_config.DatetimeColumn("Created", format="MMM D YYYY"),
        }
    )
else:
    st.info("No models found.")

st.divider()

# ── Model versions ────────────────────────────────────────
st.subheader("Model Versions")

versions = query("""
    SELECT m.model_name, mv.version_no, mv.algorithm,
           mv.status, mv.created_at
    FROM model_version mv
    JOIN model m ON mv.model_id = m.model_id
    ORDER BY m.model_name, mv.version_no
""")

if versions:
    st.dataframe(
        pd.DataFrame(versions),
        use_container_width=True,
        hide_index=True,
        column_config={
            "model_name": st.column_config.TextColumn("Model"),
            "version_no": st.column_config.TextColumn("Version", width="small"),
            "algorithm":  st.column_config.TextColumn("Algorithm"),
            "status":     st.column_config.TextColumn("Status"),
            "created_at": st.column_config.DatetimeColumn("Created", format="MMM D YYYY"),
        }
    )
else:
    st.info("No versions found.")