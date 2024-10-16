import streamlit as st
import os

from template import translation_prompt
from chat import Chat

if st.session_state.login:
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL")

    model = "deepseek-ai/DeepSeek-V2.5"
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 0.7
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

    c = Chat(api_key=api_key, base_url=base_url)

    st.subheader("Translator", anchor=False)

    if "source_text" not in st.session_state:
        st.session_state.source_text = ""

    if "trans_msg" not in st.session_state:
        st.session_state.trans_msg = []
    
    if "trans" not in st.session_state:
        st.session_state.trans = False

    if not st.session_state.trans_msg:
        source_text: str = st.text_input("Source Text", st.session_state.source_text, key="source")
        st.session_state.source_text = source_text
        translate_btn: bool = st.button("Translate", "translate_btn", type="primary", disabled=not source_text)
        if translate_btn:
            st.session_state.trans_msg = []
            st.session_state.trans = True
            st.rerun()
    else:
        trans_clear_btn = st.button("Clear", "trans_clear_btn", disabled=st.session_state.trans_msg==[])
        if trans_clear_btn:
            st.session_state.source_text = ""
            st.session_state.trans_msg = []
            st.rerun()

    if st.session_state.trans_msg:
        st.markdown(st.session_state.trans_msg[0]["content"])

    if st.session_state.trans:
        messages: list = [{"role": "system", "content": translation_prompt}, {"role": "user", "content": source_text}]
        response = c.default_chat(model, messages, max_tokens, temperature, top_p, frequency_penalty, presence_penalty)
        result: str = st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
        st.session_state.trans_msg.append({"role": "assistant", "content": result})
        st.session_state.source_text = ""
        st.session_state.trans = False
        st.rerun()