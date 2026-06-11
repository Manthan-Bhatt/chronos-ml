import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from db import query

st.set_page_config(page_title="Training Runs", page_icon="▶", layout="wide")

st.title("▶ Training Runs")
st.divider()

# ── Run selector in sidebar ───────────────────────────────
st.sidebar.header("Select a Run")

runs = query("""
    SELECT r.run_id, m.model_name, r.status, r.created_at
    FROM training_run r
    JOIN model m ON r.model_id = m.model_id
    ORDER BY r.created_at DESC
""")

if not runs:
    st.info("No training runs found.")
    st.stop()

run_labels = {
    f"{r['model_name']} — {str(r['run_id'])[:8]} ({r['status']})": r["run_id"]
    for r in runs
}
selected_label = st.sidebar.selectbox("Run", list(run_labels.keys()))
selected_id = run_labels[selected_label]

# ── Run metadata ──────────────────────────────────────────
run = query("""
    SELECT r.*, m.model_name, mv.algorithm
    FROM training_run r
    JOIN model m ON r.model_id = m.model_id
    JOIN model_version mv
      ON r.model_id = mv.model_id
     AND r.version_no = mv.version_no
    WHERE r.run_id = %s
""", (selected_id,))[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Model",     run["model_name"])
col2.metric("Algorithm", run["algorithm"])
col3.metric("Version",   run["version_no"])
col4.metric("Status",    run["status"])

if run["start_time"] and run["end_time"]:
    duration = run["end_time"] - run["start_time"]
    st.caption(f"Duration: {str(duration).split('.')[0]}")

st.divider()

# ── Metrics chart ─────────────────────────────────────────
st.subheader("Evaluation Metrics Over Time")

metrics = query("""
    SELECT snapshot_id, accuracy, f1_score, recall,
           precision_score, validation_loss
    FROM evaluation_metric
    WHERE run_id = %s
    ORDER BY snapshot_id
""", (selected_id,))

if metrics:
    df = pd.DataFrame(metrics)

    # Score metrics (left y-axis)
    fig = go.Figure()
    for col, color, name in [
        ("accuracy",         "#185FA5", "Accuracy"),
        ("f1_score",         "#1D9E75", "F1 Score"),
        ("recall",           "#BA7517", "Recall"),
        ("precision_score",  "#533AB7", "Precision"),
    ]:
        fig.add_trace(go.Scatter(
            x=df["snapshot_id"], y=df[col],
            name=name,
            line=dict(color=color, width=2),
            mode="lines+markers",
            marker=dict(size=5)
        ))

    # Validation loss (right y-axis)
    fig.add_trace(go.Scatter(
        x=df["snapshot_id"], y=df["validation_loss"],
        name="Val. Loss",
        line=dict(color="#E05252", width=2, dash="dash"),
        mode="lines+markers",
        marker=dict(size=5),
        yaxis="y2"
    ))

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_family="sans-serif",
        legend=dict(orientation="h", y=-0.2),
        xaxis=dict(title="Snapshot", gridcolor="#F0EEE8"),
        yaxis=dict(title="Score (0–1)", range=[0, 1], gridcolor="#F0EEE8"),
        yaxis2=dict(title="Val. Loss", overlaying="y", side="right",
                    gridcolor="#F0EEE8"),
        margin=dict(l=0, r=0, t=10, b=0),
        height=350,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Best snapshot summary
    best = df.loc[df["f1_score"].idxmax()]
    st.caption(f"Best snapshot: #{int(best['snapshot_id'])} — "
               f"F1: {best['f1_score']:.4f} | "
               f"Accuracy: {best['accuracy']:.4f} | "
               f"Val. Loss: {best['validation_loss']:.4f}")
else:
    st.info("No evaluation metrics recorded for this run.")

st.divider()

# ── Hyperparameters ───────────────────────────────────────
st.subheader("Hyperparameters")

params = query("""
    SELECT parameter_name, data_type, value
    FROM hyperparameter
    WHERE run_id = %s
    ORDER BY parameter_name
""", (selected_id,))

if params:
    st.dataframe(
        pd.DataFrame(params),
        use_container_width=True,
        hide_index=True,
        column_config={
            "parameter_name": st.column_config.TextColumn("Parameter"),
            "data_type":      st.column_config.TextColumn("Type", width="small"),
            "value":          st.column_config.TextColumn("Value"),
        }
    )
else:
    st.info("No hyperparameters recorded for this run.")

st.divider()

# ── Datasets used ─────────────────────────────────────────
st.subheader("Datasets Used")

datasets = query("""
    SELECT d.dataset_name, du.version_no,
           du.split_type, dv.num_rows, dv.num_features
    FROM dataset_used du
    JOIN dataset d ON du.dataset_id = d.dataset_id
    JOIN dataset_version dv
      ON du.dataset_id = dv.dataset_id
     AND du.version_no = dv.version_no
    WHERE du.run_id = %s
""", (selected_id,))

if datasets:
    st.dataframe(
        pd.DataFrame(datasets),
        use_container_width=True,
        hide_index=True,
        column_config={
            "dataset_name": st.column_config.TextColumn("Dataset"),
            "version_no":   st.column_config.TextColumn("Version", width="small"),
            "split_type":   st.column_config.TextColumn("Split"),
            "num_rows":     st.column_config.NumberColumn("Rows", format="%d"),
            "num_features": st.column_config.NumberColumn("Features", format="%d"),
        }
    )
else:
    st.info("No datasets linked to this run.")