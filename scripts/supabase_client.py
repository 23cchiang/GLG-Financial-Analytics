from supabase import create_client
import streamlit as st

print("URL:", st.secrets["supabase_url"])

supabase = create_client(
    st.secrets["supabase_url"],
    st.secrets["supabase_key"]
)