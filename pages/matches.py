"""
View Matches Page.

Auth required.
"""

import streamlit as st
import auth
import matches
import database

st.set_page_config(
    page_title="My Matches",
)

auth.require_auth()
