import psycopg2
import psycopg2.extras
import streamlit as st

def get_conn():
    return psycopg2.connect(
        st.secrets["DATABASE_URL"],
        cursor_factory=psycopg2.extras.RealDictCursor
    )

def query(sql, params=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SET search_path TO chronos_ml")
            cur.execute(sql, params or ())
            return cur.fetchall()