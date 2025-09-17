# -*- coding: utf-8 -*-
"""
AI Prompt Engineer: A Streamlit Web App

Main entry point for the Streamlit application. This file handles page routing,
initial configuration, and styling.
"""

# --- IMPORTS ---
import streamlit as st
from ui_components import main_app_page, admin_page

# --- PAGE CONFIGURATION ---
# Set page configuration for a mobile-first, responsive layout.
# This should be the first Streamlit command in the script.
st.set_page_config(
    page_title="AI Prompt Engineer",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="auto",
)

# --- STYLING ---
# Custom CSS to improve the mobile-first design and aesthetics.
st.markdown("""
<style>
    /* General styles */
    .stApp {
        background-color: #f0f2f6;
    }
    /* Style for buttons */
    .stButton > button {
        border-radius: 12px;
        border: 2px solid #1E88E5;
        color: #1E88E5;
        background-color: #FFFFFF;
        transition: all 0.2s ease-in-out;
        font-weight: bold;
    }
    .stButton > button:hover {
        border-color: #1565C0;
        color: #FFFFFF;
        background-color: #1E88E5;
    }
    .stButton > button:active {
        background-color: #1565C0;
        border-color: #1565C0;
    }
    /* Style for generated prompt code block */
    div[data-testid="stCodeBlock"] {
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    /* Responsive textareas */
    .stTextArea textarea {
        min-height: 150px;
    }
    h1, h2, h3 {
        color: #1565C0;
    }
</style>
""", unsafe_allow_html=True)


# --- NAVIGATION ---
def main():
    """Main function to handle page navigation."""
    st.sidebar.title("Navigation")
    page_options = {
        "Prompt Generator": main_app_page,
        "Admin Panel": admin_page
    }
    page_selection = st.sidebar.radio("Choose a page", list(page_options.keys()))

    # Run the selected page function
    page_options[page_selection]()

if __name__ == "__main__":
    main()

