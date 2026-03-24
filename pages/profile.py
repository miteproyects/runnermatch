"""
Manage User Profile Page.
"""

import streamlit as st
import auth
import profile
import verification

auth.require_auth()
