import streamlit as st
import base64
import os

from model_config import ModelConfig
from chat import Chat

if st.session_state.login:
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL")

    mc = ModelConfig()
    model_list: list = mc.image_model_list()

    c = Chat(api_key=api_key, base_url=base_url)

    st.subheader("Image Chatbot", anchor=False)

    if "message" not in st.session_state:
        st.session_state.message = []
    
    if "memory" not in st.session_state:
        st.session_state.memory = []
    
    if "regen" not in st.session_state:
        st.session_state.regen = False
    
    with st.sidebar:
        model: str = st.selectbox("Model", model_list, 0, key="img_model", disabled=st.session_state.message!=[])
        newchat_btn: bool = st.button("New Chat", key="newchat_btn", type="primary", disabled=st.session_state.message==[], use_container_width=True)
        withdraw_btn: bool = st.button("Withdraw", key="withdraw_btn", disabled=st.session_state.message==[], use_container_width=True)
        regen_btn: bool = st.button("Regenerate", key="regen_btn", disabled=st.session_state.memory==[] or st.session_state.memory[-1]["role"]!="assistant", use_container_width=True)
        with st.expander("Parameter Settings"):
            max_tokens: int = st.slider("Max Tokens", 1, 4096, 4096, 1, key="img_tokens", disabled=st.session_state.message!=[])
            temperature: float = st.slider("Temperature", 0.0, 2.0, 0.7, 0.01, key="img_temp", disabled=st.session_state.message!=[])
            top_p: float = st.slider("Top P", 0.0, 1.0, 0.7, 0.01, key="img_top_p", disabled=st.session_state.message!=[])
            frequency_penalty: float = st.slider("Frequency Penalty", -2.0, 2.0, 0.0, 0.01, key="img_freq_pen", disabled=st.session_state.message!=[])
            presence_penalty: float = st.slider("Presence Penalty", -2.0, 2.0, 0.0, 0.01, key="img_pres_pen", disabled=st.session_state.message!=[])
        
    img_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], key="img_file", disabled=st.session_state.message!=[])
    if img_file is not None:
        with st.expander("Image Preview"):
            st.image(img_file)
        img_type = img_file.name.split(".")[-1].lower()
        img_bytes = img_file.read()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        img_url = f"data:image/{img_type};base64,{img_b64}"
    
    for i in st.session_state.memory:
        with st.chat_message(i["role"]):
            st.markdown(i["content"])
    
    if query := st.chat_input("Say something...", key="img_query", disabled=not st.session_state.login):
        st.session_state.message.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        if len(st.session_state.message) == 1:
            messages: list = [
                {"role": "user", "content": [
                    {"type": "text", "text": query},
                    {"type": "image_url", "image_url": {"url": img_url}}]}]
        else:
            messages: list = [
                {"role": "user", "content": [
                    {"type": "text", "text": st.session_state.message[0]["content"]},
                    {"type": "image_url", "image_url": {"url": img_url}}]}] + st.session_state.message[1:]
        
        with st.chat_message("assistant"):
            response = c.default_chat(model, messages, max_tokens, temperature, top_p, frequency_penalty, presence_penalty)
            result: str = st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
            st.session_state.message.append({"role": "assistant", "content": result})
            st.session_state.memory = st.session_state.message
        st.rerun()
    
    if newchat_btn:
        st.session_state.message = []
        st.session_state.memory = []
        st.rerun()
    
    if withdraw_btn:
        del st.session_state.message[-1]
        del st.session_state.memory[-1]
        st.rerun()
    
    if regen_btn:
        st.session_state.message.pop()
        st.session_state.memory = []
        st.session_state.regen = True
        st.rerun()
    if st.session_state.regen:
        for i in st.session_state.message:
            with st.chat_message(i["role"]):
                st.markdown(i["content"])
    
        if len(st.session_state.message) == 1:
            messages: list = [
                {"role": "user", "content": [
                    {"type": "text", "text": query},
                    {"type": "image_url", "image_url": {"url": img_url}}]}]
        else:
            messages: list = [
                {"role": "user", "content": [
                    {"type": "text", "text": st.session_state.message[0]["content"]},
                    {"type": "image_url", "image_url": {"url": img_url}}]}] + st.session_state.message[1:]
        
        with st.chat_message("assistant"):
            response = c.default_chat(model, messages, max_tokens, temperature, top_p, frequency_penalty, presence_penalty)
            result: str = st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
            st.session_state.message.append({"role": "assistant", "content": result})
            st.session_state.memory = st.session_state.message
            st.session_state.regen = False
        st.rerun()