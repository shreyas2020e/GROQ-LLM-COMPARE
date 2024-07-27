import streamlit as st
import time
from groq import Groq
import os
import asyncio
import aiohttp


api_key = st.secrets["GROQ_API_KEY"]

# Define the taglines
taglines = [
    "Compare: Fast and Efficient Language Models",
    "Unlock the Power of AI with Compare",
    "Experience Lightning-Fast Responses",
    "Compare: Your AI Companion"
]

# Define the models
models = {
    "Meta Llama 3 8B": "llama3-8b-8192",
    "Meta Llama 3 70B": "llama3-70b-8192",
    "Mixtral 8x7B": "mixtral-8x7b-32768",
    "Gemma 7B": "gemma-7b-it",
    "Gemma 2 9B": "gemma2-9b-it"
}


async def get_response(prompt, model_id, session):
    try:
        async with session.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model_id,
                "messages": [{"role": "user", "content": prompt}]
            }
        ) as response:
            data = await response.json()
            return data['choices'][0]['message']['content']
    except Exception as e:
        return f"An error occurred: {str(e)}"

async def get_all_responses(prompt):
    async with aiohttp.ClientSession() as session:
        tasks = [get_response(prompt, model_id, session) for model_id in models.values()]
        return await asyncio.gather(*tasks)

# Set up the Streamlit page
st.set_page_config(page_title="Compare - LLM Models", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS
st.markdown("""
    <style>
    .response-box {
        background-color: #2e2c27;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
        height: 300px;
        overflow-y: auto;
    }
    .model-name {
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("Model Information")
    for model_name, model_id in models.items():
        st.write(f"**{model_name}:** {model_id}")

# Create a container for the dynamic tagline
tagline_container = st.empty()

# Main content
st.title("Compare -  LLM Models")

# Input prompt
user_prompt = st.text_area("Enter your prompt:", height=100)

# Submit button
if st.button("Submit to All Models"):
    if user_prompt:
        with st.spinner("Generating responses from all models..."):
            responses = asyncio.run(get_all_responses(user_prompt))
        st.session_state.responses = dict(zip(models.keys(), responses))
    else:
        st.warning("Please enter a prompt.")

# Display responses in a grid
if 'responses' in st.session_state:
    st.subheader("Model Responses")
    
    # Create rows with two columns each
    for i in range(0, len(models), 2):
        col1, col2 = st.columns(2)
        
        with col1:
            if i < len(models):
                model_name = list(models.keys())[i]
                response = st.session_state.responses[model_name]
                st.markdown(f"<div class='model-name'>{model_name}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='response-box'>{response}</div>", unsafe_allow_html=True)
        
        with col2:
            if i + 1 < len(models):
                model_name = list(models.keys())[i + 1]
                response = st.session_state.responses[model_name]
                st.markdown(f"<div class='model-name'>{model_name}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='response-box'>{response}</div>", unsafe_allow_html=True)

# Dynamic tagline
def rotate_tagline():
    while True:
        for tagline in taglines:
            tagline_container.markdown(f"<h3 style='text-align: center;'>{tagline}</h3>", unsafe_allow_html=True)
            time.sleep(3)

# Run the tagline rotation in a separate thread
import threading
tagline_thread = threading.Thread(target=rotate_tagline)
tagline_thread.daemon = True
tagline_thread.start()

# Footer
st.markdown("---")
st.markdown("Powered by GROQ - Fast Inference for Language Models")