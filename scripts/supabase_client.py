from supabase import create_client
import streamlit as st

superbase = create_client(
    st.secrets["superbase_url"],
    st.secrets["superbase_key"]
)