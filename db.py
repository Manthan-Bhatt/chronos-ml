import psycopg2
import psycopg2.extras
import streamlit as st

def get_conn():
    return psycopg2.connect(
        host=st.secrets["localhost"],
        dbname=st.secrets["postgres"],
        user=st.secrets["postgres"],
        password=st.secrets["Manthan_Bhatt"],
        port=st.secrets["5432"],
        cursor_factory=psycopg2.extras.RealDictCursor,
        options="-c search_path=chronos_ml"
    )

def query(sql, params=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()