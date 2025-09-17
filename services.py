# -*- coding: utf-8 -*-
"""
Services Module

This file handles all interactions with external APIs, including OpenAI and Airtable.
It separates the core business logic from the UI.
"""

# --- IMPORTS ---
import streamlit as st
import openai
from pyairtable import Api
import config  # Import configuration variables

# --- CLIENT INITIALIZATION ---
try:
    # Initialize OpenAI client
    if config.OPENAI_API_KEY and config.OPENAI_API_KEY != "YOUR_OPENAI_API_KEY_HERE":
        openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    else:
        openai_client = None
        st.warning("OpenAI API Key not configured. AI features will be disabled.", icon="⚠️")

    # Initialize Airtable client
    if all([
        config.AIRTABLE_API_KEY != "YOUR_AIRTABLE_API_KEY_HERE",
        config.AIRTABLE_BASE_ID != "YOUR_AIRTABLE_BASE_ID_HERE",
        config.AIRTABLE_TABLE_NAME != "YOUR_AIRTABLE_TABLE_NAME_HERE"
    ]):
        airtable_api = Api(config.AIRTABLE_API_KEY)
        airtable_table = airtable_api.table(config.AIRTABLE_BASE_ID, config.AIRTABLE_TABLE_NAME)
    else:
        airtable_table = None
        st.warning("Airtable credentials not fully configured. Data storage will be disabled.", icon="⚠️")

except Exception as e:
    st.error(f"Failed to initialize API clients. Please check your credentials. Error: {e}")
    st.stop()


# --- HELPER FUNCTIONS ---

def call_openai_api(system_prompt, user_prompt):
    """
    Generic function to call the OpenAI ChatCompletion API.
    It uses the model name specified in the config.py file.
    """
    if not openai_client:
        st.error("OpenAI client is not initialized. Cannot call API.")
        return None

    try:
        response = openai_client.chat.completions.create(
            model=config.OPENAI_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=1500,
        )
        return response.choices[0].message.content.strip()
    except openai.APIError as e:
        st.error(f"An OpenAI API error occurred: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred while calling OpenAI: {e}")
    return None

def save_to_airtable(data):
    """Saves a dictionary of data to the configured Airtable table."""
    if not airtable_table:
        st.warning("Airtable is not configured. Data not saved.")
        return False
    try:
        airtable_table.create(data)
        st.toast("Prompt saved to Airtable!", icon="📄")
        return True
    except Exception as e:
        st.error(f"Failed to save data to Airtable: {e}")
        return False

def fetch_from_airtable():
    """Fetches all records from the configured Airtable table."""
    if not airtable_table:
        st.warning("Airtable is not configured. Cannot fetch data.")
        return []
    try:
        return airtable_table.all()
    except Exception as e:
        st.error(f"Failed to fetch data from Airtable: {e}")
        return []


