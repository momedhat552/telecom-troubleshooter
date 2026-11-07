import streamlit as st
from agent import run_agent

MAX_QUESTIONS = 10  # protects your API quota on a public demo

st.set_page_config(page_title="Telecom Troubleshooter")
st.title("Telecom Troubleshooter")
st.caption("Ask about indoor coverage, path loss, units. It searches the documents and calls calculator tools.")

if "count" not in st.session_state:
    st.session_state.count = 0

question = st.chat_input("e.g. Why does 5G drop indoors? What is the path loss for 50 m at 3500 MHz?")

if question:
    with st.chat_message("user"):
        st.write(question)

    if st.session_state.count >= MAX_QUESTIONS:
        st.warning("Demo limit reached for this session.")
    else:
        st.session_state.count += 1
        with st.chat_message("assistant"):
            try:
                with st.spinner("Thinking..."):
                    answer, steps = run_agent(question)
                st.markdown(answer)
                if steps:
                    with st.expander("Show your work: tools used"):
                        for s in steps:
                            st.markdown(f"**{s['tool']}** `{s['args']}`")
                            st.code(s["result"][:800])
            except Exception as e:
                st.error(f"Something went wrong: {e}")