import streamlit as st
import ollama

@st.cache_resource
def get_client():
    # Return a cached resource or client if needed
    return True

st.setTitle = st.title("Ollama")
prompt = st.text_area(label="Enter your text here")
button = st.button(label="Click here")

if button:
    response = ollama.generate(model="llama3.1", prompt=prompt)
    st.markdown(response['response'], unsafe_allow_html=True)