"""
RunnerMatch - Profile Page
Create and edit user profile with mandatory height/weight.
"""

import datetime
import streamlit as st
from i18n import t
import auth
from database import get_db, User, Profile, Photo
