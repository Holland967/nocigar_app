import streamlit as st
import os

from model_config import ModelConfig
from template import default_prompt
from chat import Chat

pass_word = os.getenv("PASS_WORD")

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    password: str = st.text_input("Password", "", key="password", type="password")
    login_btn: bool = st.button("Login", key="login_btn", type="primary", disabled=not password)
    if login_btn:
        if password == pass_word:
            st.session_state.login = True
            st.rerun()

if st.session_state.login:
    st.subheader("General Chat", anchor=False)

    mc = ModelConfig()
    model_list: list = mc.general_model_list()

    if "msg" not in st.session_state:
        st.session_state.msg = []
    
    if "mem" not in st.session_state:
        st.session_state.mem = []
    
    if "sys" not in st.session_state:
        st.session_state.sys = default_prompt
    
    if "state" not in st.session_state:
        st.session_state.state = False
    
    with st.sidebar:
        model: str = st.selectbox("Model", model_list, 0, key="model", disabled=st.session_state.msg!=[])
        clear_btn: bool = st.button("Clear", "clear_btn", type="primary", disabled=st.session_state.msg==[], use_container_width=True)
        undo_btn: bool = st.button("Undo", "undo_btn", disabled=st.session_state.msg==[], use_container_width=True)
        retry_btn: bool = st.button("Retry", "retry_btn", disabled=st.session_state.mem==[] or st.session_state.mem[-1]["role"]!="assistant", use_container_width=True)
        system_prompt: str = st.text_area("System Prompt", st.session_state.sys, key="system_prompt", disabled=st.session_state.msg!=[])
        st.session_state.sys = system_prompt
        with st.expander("Parameter Settings"):
            max_tokens: int = st.slider("Max Tokens", 1, 4096, 4096, 1, key="max_tokens", disabled=st.session_state.msg!=[])
            temperature: float = st.slider("Temperature", 0.0, 2.0, 0.7, 0.01, key="temperature", disabled=st.session_state.msg!=[])
            top_p: float = st.slider("Top P", 0.0, 1.0, 1.0, 0.01, key="top_p", disabled=st.session_state.msg!=[])
            frequency_penalty: float = st.slider("Frequency Penalty", -2.0, 2.0, 0.0, 0.01, key="frequency_penalty", disabled=st.session_state.msg!=[])
            presence_penalty: float = st.slider("Presence Penalty", -2.0, 2.0, 0.0, 0.01, key="presence_penalty", disabled=st.session_state.msg!=[])
    
    if model == "yi-lightning":
        api_key: str = os.getenv("YI_API_KEY")
        base_url: str = os.getenv("YI_BASE_URL")
    else:
        api_key: str = os.getenv("API_KEY")
        base_url: str = os.getenv("BASE_URL")
    
    c = Chat(api_key=api_key, base_url=base_url)
    
    for i in st.session_state.mem:
        with st.chat_message(i["role"]):
            st.markdown(i["content"])
    
    if query := st.chat_input("Say something...", key="query", disabled=not st.session_state.login):
        st.session_state.msg.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)
        messages: list = [{"role": "system", "content": system_prompt}] + st.session_state.msg
        with st.chat_message("assistant"):
            response = c.default_chat(model, messages, max_tokens, temperature, top_p, frequency_penalty, presence_penalty)
            result: str = st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
            st.session_state.msg.append({"role": "assistant", "content": result})
            st.session_state.mem = st.session_state.msg
        st.rerun()
    
    if clear_btn:
        st.session_state.msg = []
        st.session_state.mem = []
        st.session_state.sys = default_prompt
        st.rerun()
    
    if undo_btn:
        del st.session_state.msg[-1]
        del st.session_state.mem[-1]
        st.rerun()
    
    if retry_btn:
        st.session_state.msg.pop()
        st.session_state.mem = []
        st.session_state.state = True
        st.rerun()
    if st.session_state.state:
        for i in st.session_state.msg:
            with st.chat_message(i["role"]):
                st.markdown(i["content"])
        messages: list = [{"role": "system", "content": system_prompt}] + st.session_state.msg
        with st.chat_message("assistant"):
            response = c.default_chat(model, messages, max_tokens, temperature, top_p, frequency_penalty, presence_penalty)
            result: str = st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
            st.session_state.msg.append({"role": "assistant", "content": result})
            st.session_state.mem = st.session_state.msg
        st.session_state.state = False
        st.rerun()