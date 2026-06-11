import streamlit as st
import pandas as pd
from db import query

st.set_page_config(page_title="Datasets", page_icon="🗄", layout="wide")

st.title("🗄 Datasets")
st.divider()

# ── Datasets table ────────────────────────────────────────
datasets = query("""
    SELECT dataset_id, dataset_name, status, source,
           is_public, created_at
    FROM dataset
    ORDER BY created_at DESC
""")

st.subheader(f"All Datasets ({len(datasets)})")

if datasets:
    st.dataframe(
        pd.DataFrame(datasets),
        use_container_width=True,
        hide_index=True,
        column_config={
            "dataset_id":   st.column_config.TextColumn("ID"),
            "dataset_name": st.column_config.TextColumn("Name"),
            "status":       st.column_config.TextColumn("Status"),
            "source":       st.column_config.TextColumn("Source"),
            "is_public":    st.column_config.CheckboxColumn("Public"),
            "created_at":   st.column_config.DatetimeColumn("Created", format="MMM D YYYY"),
        }
    )
else:
    st.info("No datasets found.")

st.divider()

# ── Dataset versions ──────────────────────────────────────
st.subheader("Dataset Versions")

versions = query("""
    SELECT d.dataset_name, dv.version_no, dv.num_rows,
           dv.num_features, dv.changelog, dv.created_at
    FROM dataset_version dv
    JOIN dataset d ON dv.dataset_id = d.dataset_id
    ORDER BY d.dataset_name, dv.version_no
""")

if versions:
    st.dataframe(
        pd.DataFrame(versions),
        use_container_width=True,
        hide_index=True,
        column_config={
            "dataset_name": st.column_config.TextColumn("Dataset"),
            "version_no":   st.column_config.TextColumn("Version", width="small"),
            "num_rows":     st.column_config.NumberColumn("Rows",     format="%d"),
            "num_features": st.column_config.NumberColumn("Features", format="%d"),
            "changelog":    st.column_config.TextColumn("Changelog"),
            "created_at":   st.column_config.DatetimeColumn("Created", format="MMM D YYYY"),
        }
    )
else:
    st.info("No dataset versions found.")