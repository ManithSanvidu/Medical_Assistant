import requests
import streamlit as st
from utils.api import api_unreachable_message, upload_pdfs_api


def render_uploader():
    st.sidebar.header("Upload Medical documents (.PDFs)")
    uploaded_files=st.sidebar.file_uploader("Upload multiple PDFs",type="pdf",accept_multiple_files=True)
    if st.sidebar.button("Upload DB") and uploaded_files:
        try:
            response = upload_pdfs_api(uploaded_files)
        except requests.exceptions.ConnectionError:
            st.sidebar.error(api_unreachable_message())
            return
        except requests.exceptions.RequestException as e:
            st.sidebar.error(f"Request failed: {e}")
            return

        if response.status_code == 200:
            st.sidebar.success("Uploaded successfully")
        else:
            st.sidebar.error(f"Error:{response.text}")