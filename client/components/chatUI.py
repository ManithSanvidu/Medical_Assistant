import requests
import streamlit as st
from utils.api import api_unreachable_message, ask_question

def render_chat():
    st.subheader("💭 Chat with your assistant")

    if "messages" not in st.session_state:
        st.session_state.messages=[]

    #render existing chat history
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).markdown(msg["content"])

    #input and response
    user_input=st.chat_input("Type your question....")
    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role":"user","content":user_input})

        try:
            response = ask_question(user_input)
        except requests.exceptions.ConnectionError:
            st.error(api_unreachable_message())
            return
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
            return

        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer")
            sources = data.get("sources", [])
            st.chat_message("assistant").markdown(answer)
            # if sources:
            #   st.markdown("📝 **Sources: **")
            #    for src in sources:
            #        st.markdown(f"=`{src}`")
            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )
        else:
            st.error(f"Error:{response.text}")