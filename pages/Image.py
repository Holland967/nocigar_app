from image_process import process_image
from openai import OpenAI
import streamlit as st
import base64
import os

if st.session_state.login:
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL")
    model_list = ["Qwen/Qwen2-VL-72B-Instruct", "OpenGVLab/InternVL2-Llama3-76B"]

    if "message" not in st.session_state:
        st.session_state.message = []

    with st.sidebar:
        clear: bool = st.button("Clear", "clear", type="primary", \
            use_container_width=True, disabled=st.session_state.message==[])
        model = st.selectbox("Model", model_list, key="model", index=0, disabled=st.session_state.message!=[])
        with st.expander("Parameter Settings"):
            max_tokens = st.slider("Max Tokens", 1, 4096, 4096, 1, key="max_tokens", disabled=st.session_state.message!=[])
            temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.01, key="temperature", disabled=st.session_state.message!=[])
            top_p = st.slider("Top P", 0.0, 1.0, 0.7, 0.01, key="top_p", disabled=st.session_state.message!=[])
            frequency_penalty = st.slider("Frequency Penalty", -2.0, 2.0, 0.0, 0.01, key="frequency_penalty", disabled=st.session_state.message!=[])
            presence_penalty = st.slider("Presence Penalty", -2.0, 2.0, 0.0, 0.01, key="presence_penalty", disabled=st.session_state.message!=[])

    image_file = st.file_uploader("Image", type=["png", "jpg", "jpeg"], \
        key="image", label_visibility="collapsed")

    if image_file is not None:
        image_data = image_file.read()
        processed_data = process_image(image_data)
        processed_data = base64.b64encode(processed_data).decode("utf-8")
        processed_data = f"data:image/jpeg;base64,{processed_data}"
        with st.expander("Image Preview"):
            st.image(processed_data)

    for i in st.session_state.message:
        with st.chat_message(i["role"]):
            st.markdown(i["content"])

    if query := st.chat_input("Say something", key="query", disabled=not image_file):
        st.session_state.message.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)
        
        if len(st.session_state.message) == 1:
            messages = [
                {"role": "user", "content": [
                    {"type": "text", "text": query},
                    {"type": "image_url", "image_url": {"url": processed_data}}]}]
        else:
            messages = [
                {"role": "user", "content": [
                    {"type": "text", "text": st.session_state.message[0]["content"]},
                    {"type": "image_url", "image_url": {"url": processed_data}}
                ]}] + st.session_state.message[1:]
        
        with st.chat_message("assistant"):
            with st.spinner("Sending image..."):
                client = OpenAI(api_key=api_key, base_url=base_url)
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                    stream=True)
            result = st.write_stream(chunk.choices[0].delta.content for chunk in response if \
                chunk.choices[0].delta.content is not None)
        
        st.session_state.message.append({"role": "assistant", "content": result})
        st.rerun()

    if clear:
        st.session_state.message = []
        st.rerun()