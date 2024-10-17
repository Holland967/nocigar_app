import streamlit as st
import os

from model_config import ModelConfig
from template import spider_prompt
from spider import Spider
from chat import Chat

if st.session_state.login:
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL")

    mc = ModelConfig()
    model_list = mc.spider_model_list()
    s = Spider()

    st.subheader("Article Summary and Analysis", anchor=False)

    if "result" not in st.session_state:
        st.session_state.result = []
    
    if "cache" not in st.session_state:
        st.session_state.cache = []
    
    if "spider_sys" not in st.session_state:
        st.session_state.spider_sys = spider_prompt

    if "webpage_content" not in st.session_state:
        st.session_state.webpage_content = ""
    
    if "refresh" not in st.session_state:
        st.session_state.refresh = False

    if "continue_" not in st.session_state:
        st.session_state.continue_ = False

    with st.sidebar:
        model: str = st.selectbox("Model", model_list, key="spider_model", disabled=st.session_state.result!=[])
        reset_btn: bool = st.button("Reset", "reset_btn", type="primary", disabled=st.session_state.result==[], use_container_width=True)
        back_btn: bool = st.button("Back", "back_btn", disabled=st.session_state.result==[], use_container_width=True)
        refresh_btn: bool = st.button("Refresh", "refresh_btn", disabled=st.session_state.cache==[] or st.session_state.cache[-1]["role"]!="assistant", use_container_width=True)
        with st.expander("Parameter Settings"):
            max_tokens: int = st.slider("Max Tokens", 1, 4096, 4096, 1, key="spider_tokens", disabled=st.session_state.result!=[])
            temperature: float = st.slider("Temperature", 0.0, 2.0, 0.5, 0.01, key="spider_temp", disabled=st.session_state.result!=[])
            top_p: float = st.slider("Top P", 0.0, 1.0, 0.7, 0.01, key="spider_top_p", disabled=st.session_state.result!=[])
            frequency_penalty: float = st.slider("Frequency Penalty", -2.0, 2.0, 0.0, 0.01, key="spider_freq_pen", disabled=st.session_state.result!=[])
            presence_penalty: float = st.slider("Presence Penalty", -2.0, 2.0, 0.0, 0.01, key="spider_pres_pen", disabled=st.session_state.result!=[])
        spider_system: str = st.text_area("System Prompt", st.session_state.spider_sys, height=200, key="spider_system", disabled=st.session_state.result!=[])
        st.session_state.spider_sys = spider_system
    
    if st.session_state.cache:
        with st.expander("Article Preview"):
            st.markdown(st.session_state.cache[0]["content"])
    for i in st.session_state.cache[1:]:
        with st.chat_message(i["role"]):
            st.markdown(i["content"])
    
    if query := st.chat_input("Say something...", key="spider_query", disabled=not st.session_state.login):
        if st.session_state.result == []:
            with st.spinner("Crawling the web..."):
                link_type: str = s.check_url(query)
                if link_type == "gzh":
                    text: str = s.gzh_spider(query)
                elif link_type == "rmw":
                    text: str = s.rmw_spider(query)
                elif link_type == "xhw":
                    text: str = s.xhw_spider(query)
                elif link_type == "gmw":
                    text: str = s.gmw_spider(query)
                elif link_type == "cnyt":
                    text: str = s.cnyt_spider(query)
                elif link_type == "general":
                    text: str = s.general_spider(query)
                st.session_state.webpage_content = text
                if len(text) < 8000:
                    st.session_state.result.append({"role": "user", "content": st.session_state.webpage_content})
                    st.session_state.continue_ = True
                    with st.expander("Content Preview"):
                        st.markdown(st.session_state.webpage_content)
                else:
                    st.warning(f"Character Length: {len(text)}. Do you continue?")
                    with st.expander("Content Preview"):
                        st.markdown(st.session_state.webpage_content)
                    if st.button("Yes", "yes", type="primary"):
                        st.session_state.result.append({"role": "user", "content": st.session_state.webpage_content})
                        st.session_state.continue_ = True
                    elif st.button("No", "no"):
                        st.session_state.webpage_content = ""
                        st.rerun()
        else:
            st.session_state.result.append({"role": "user", "content": query})
            st.session_state.continue_ = True
            with st.chat_message("user"):
                st.markdown(query)
        
        if st.session_state.continue_:
            messages: list = [{"role": "system", "content": spider_system}] + st.session_state.result
            with st.chat_message("assistant"):
                c = Chat(api_key=api_key, base_url=base_url)
                response = c.default_chat(model, messages, max_tokens, temperature, top_p, frequency_penalty, presence_penalty)
                result: str = st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
                st.session_state.result.append({"role": "assistant", "content": result})
                st.session_state.cache = st.session_state.result
                st.session_state.continue_ = False
            st.rerun()
    
    if reset_btn:
        st.session_state.webpage_content = ""
        st.session_state.result = []
        st.session_state.cache = []
        st.session_state.spider_sys = spider_prompt
        st.rerun()
    
    if back_btn:
        del st.session_state.result[-1]
        del st.session_state.cache[-1]
        st.rerun()
    
    if refresh_btn:
        st.session_state.result.pop()
        st.session_state.cache = []
        st.session_state.refresh = True
        st.rerun()
    if st.session_state.refresh:
        with st.spinner("Article Preview"):
            st.markdown(st.session_state.cache[0]["content"])
        for i in st.session_state.result[1:]:
            with st.chat_message(i["role"]):
                st.markdown(i["content"])
        messages: list = [{"role": "system", "content": spider_system}] + st.session_state.result
        with st.chat_message("assistant"):
            c = Chat(api_key=api_key, base_url=base_url)
            response = c.default_chat(model, messages, max_tokens, temperature, top_p, frequency_penalty, presence_penalty)
            result: str = st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
            st.session_state.result.append({"role": "assistant", "content": result})
            st.session_state.cache = st.session_state.result
        st.session_state.refresh = False
        st.rerun()
