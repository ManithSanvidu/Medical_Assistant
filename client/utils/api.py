import requests
import streamlit as st

_REQUEST_TIMEOUT = 120

# Safe API URL loading
try:
    API_URL = st.secrets["API_URL"].rstrip("/")  # remove trailing slash
except Exception:
    API_URL = None


# -------------------------------
# Upload PDFs
# -------------------------------
def upload_pdfs_api(files):
    if not API_URL:
        raise ValueError("API_URL is not set in Streamlit Secrets")

    files_payload = [
        ("files", (f.name, f.read(), "application/pdf")) for f in files
    ]

    try:
        response = requests.post(
            f"{API_URL}/upload_pdfs/",
            files=files_payload,
            timeout=_REQUEST_TIMEOUT,
        )
        return response
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Upload failed: {e}")


# -------------------------------
# ASK QUESTION (FIXED → /ask)
# -------------------------------
def ask_question(question):
    if not API_URL:
        raise ValueError("API_URL is not set in Streamlit Secrets")

    try:
        response = requests.post(
            f"{API_URL}/ask",  
            json={"question": question},  
            timeout=_REQUEST_TIMEOUT,
        )
        return response
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Request failed: {e}")


# -------------------------------
# Error Message
# -------------------------------
def api_unreachable_message() -> str:
    if not API_URL:
        return "API_URL is not configured in Streamlit Secrets."

    return (
        f"Cannot reach the API at {API_URL}. "
        "Make sure your FastAPI backend is deployed and running."
    )