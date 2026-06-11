import psycopg2
import psycopg2.extras
import streamlit as st

def get_conn():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        dbname=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASS"],
        port=5432,
        sslmode="require",
        cursor_factory=psycopg2.extras.RealDictCursor,
        options="-c search_path=chronos_ml"
    )

def query(sql, params=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()