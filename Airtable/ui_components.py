# -*- coding: utf-8 -*-
"""
UI Components Module

This file contains the functions that render the Streamlit pages for the application.
"""

# --- IMPORTS ---
import streamlit as st
import pandas as pd
import datetime
import json
from services import call_openai_api, save_to_airtable, fetch_from_airtable
from config import ADMIN_PASSWORD

# --- MAIN APPLICATION PAGE ---

def main_app_page():
    """Renders the main prompt generation page."""
    st.title("🚀 AI Prompt Engineer")
    st.markdown("Craft the perfect AI prompt by answering a few simple questions. Let AI help you build a better prompt!")

    with st.form(key="prompt_form"):
        st.subheader("1. Define Your Goal")
        goal = st.text_area(
            "What is the primary objective of your prompt? What do you want the AI to do?",
            placeholder="e.g., Generate a marketing email, write a Python script, summarize a research paper.",
            help="Be specific about the final output you expect."
        )

        st.subheader("2. Provide Context")
        context = st.text_area(
            "What background information is necessary for the AI to understand the task?",
            placeholder="e.g., Product details, target audience demographics, key points of the paper.",
            help="Imagine you're explaining the task to a new team member."
        )

        st.subheader("3. Specify the Format")
        output_format = st.text_input(
            "What structure or format should the AI's response follow?",
            placeholder="e.g., A JSON object, a list of bullet points, a 3-paragraph essay.",
            help="Examples: 'A professional email', 'A markdown table', 'A python function'."
        )

        st.subheader("4. Set the Tone & Style")
        tone = st.selectbox(
            "What tone of voice should the AI adopt?",
            ["Professional", "Casual", "Enthusiastic", "Formal", "Humorous", "Neutral", "Empathetic"],
            help="This sets the personality of the AI's response."
        )

        st.subheader("5. Add Constraints")
        constraints = st.text_area(
            "What are the 'rules' or constraints? What should the AI avoid?",
            placeholder="e.g., Do not exceed 200 words, avoid technical jargon, must include a call-to-action.",
            help="Define the boundaries for the AI."
        )

        submit_button = st.form_submit_button(label="✨ Generate My Prompt!")

    if submit_button:
        if not all([goal, context, output_format, tone]):
            st.warning("Please fill out all the required fields to generate a high-quality prompt.")
            return

        with st.spinner("Your prompt is being engineered... Please wait."):
            system_prompt_for_generation = (
                "You are an expert in prompt engineering. Your task is to synthesize user-provided components "
                "(goal, context, format, tone, constraints) into a single, comprehensive, and highly effective prompt. "
                "The final prompt should be clear, detailed, and ready to be used with a powerful AI model like GPT-5. "
                "Structure the prompt logically, often starting with the role, followed by the task, context, and clear instructions."
            )
            user_input_summary = (
                f"**Goal:**\n{goal}\n\n"
                f"**Context:**\n{context}\n\n"
                f"**Desired Format:**\n{output_format}\n\n"
                f"**Tone of Voice:**\n{tone}\n\n"
                f"**Constraints:**\n{constraints}\n"
            )

            generated_prompt = call_openai_api(system_prompt_for_generation, user_input_summary)

            if generated_prompt:
                st.session_state.generated_prompt = generated_prompt
                airtable_data = {
                    "Goal": goal, "Context": context, "Format": output_format,
                    "Tone": tone, "Constraints": constraints, "GeneratedPrompt": generated_prompt,
                    "Timestamp": datetime.datetime.utcnow().isoformat()
                }
                save_to_airtable(airtable_data)

    if "generated_prompt" in st.session_state:
        st.success("✅ Prompt successfully generated!")
        st.subheader("Your Engineered Prompt")
        
        prompt_text = st.session_state.generated_prompt
        st.code(prompt_text, language='text')

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download as .txt", data=prompt_text.encode("utf-8"),
                file_name="generated_prompt.txt", mime="text/plain", use_container_width=True,
            )
        with col2:
            st.button("📋 Copy Prompt", help="Click the copy icon on the top right of the prompt box above.", use_container_width=True, disabled=True)

# --- ADMIN PANEL PAGE ---

def admin_page():
    """Renders the password-protected admin panel."""
    st.title("🔐 Admin Panel")
    st.markdown("View user submissions and analyze prompt quality.")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        password = st.text_input("Enter Admin Password", type="password")
        if st.button("Login"):
            if password == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Incorrect password.")
        st.stop()

    st.success("Logged in successfully.")

    records = fetch_from_airtable()
    if not records:
        st.warning("No records found in Airtable or service is not configured.")
        st.stop()

    df = pd.DataFrame([record['fields'] for record in records])
    df['record_id'] = [record['id'] for record in records]
    
    display_columns = ['Timestamp', 'Goal', 'Context', 'GeneratedPrompt', 'record_id']
    df_display = df[[col for col in display_columns if col in df.columns]]
    
    st.subheader("📋 All Prompt Submissions")
    st.dataframe(df_display, use_container_width=True)

    st.header("🔬 Analyze a Single Prompt")
    selected_id = st.selectbox(
        "Select a prompt to analyze by its Record ID:",
        options=df['record_id'].tolist(),
        format_func=lambda x: f"Record ...{x[-5:]}"
    )

    if selected_id:
        selected_record = df[df['record_id'] == selected_id].iloc[0]
        prompt_to_analyze = selected_record['GeneratedPrompt']

        st.markdown("#### Selected Prompt:")
        st.code(prompt_to_analyze, language='text')

        if st.button("Analyze This Prompt"):
            with st.spinner("Running GPT-5 analysis... This may take a moment."):
                # 1. Quality Analysis
                st.subheader("📊 Quality Analysis")
                quality_system_prompt = "You are a prompt quality analysis expert..."
                quality_analysis = call_openai_api(quality_system_prompt, prompt_to_analyze)
                st.markdown(quality_analysis or "Could not generate analysis.")

                # 2. Metadata Extraction
                st.subheader("🔖 Extracted Metadata")
                metadata_system_prompt = "You are a metadata extraction AI... Return the output as a clean JSON object."
                metadata_analysis = call_openai_api(metadata_system_prompt, prompt_to_analyze)
                try:
                    st.json(json.loads(metadata_analysis))
                except (json.JSONDecodeError, TypeError):
                    st.text(metadata_analysis or "Could not extract metadata.")

                # 3. Strengths & Weaknesses Summary
                st.subheader("👍 Strengths & Weaknesses 👎")
                summary_system_prompt = "You are a strategic analyst... Provide a concise summary..."
                summary_analysis = call_openai_api(summary_system_prompt, prompt_to_analyze)
                st.markdown(summary_analysis or "Could not generate summary.")

    st.header("📈 Batch Trend Analysis")
    st.markdown("Analyze all stored prompts to identify patterns and insights.")
    if st.button("Run Batch Analysis on All Prompts"):
        with st.spinner("Analyzing trends across all prompts... This could take some time."):
            all_prompts = "\n\n---\n\n".join(df['GeneratedPrompt'].dropna().tolist())
            batch_system_prompt = "You are a data analyst specializing in AI prompt trends..."
            batch_analysis = call_openai_api(batch_system_prompt, all_prompts)
            st.subheader("Trend Analysis Report")
            st.markdown(batch_analysis or "Could not generate batch analysis.")

