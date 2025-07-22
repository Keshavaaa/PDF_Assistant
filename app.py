import streamlit as st
from backend import (
    load_pdf_text,
    get_vectorstore_from_text,
    get_qa_chain_with_memory,
    get_custom_response,
)
from prompts import summary_prompt, mcq_prompt, plan_prompt

# ---------------------------- #
#        App Initialization    #
# ---------------------------- #

def init_session_state():
    """Initialize necessary session state variables."""
    if "document_vector_index" not in st.session_state:
        st.session_state.document_content = None
        st.session_state.document_vector_index = None
        st.session_state.conversational_qa_chain = None
        st.session_state.chat_memory = None
        st.session_state.chat_history = []

# ---------------------------- #
#        PDF Upload            #
# ---------------------------- #

def upload_pdf():
    """Handle PDF upload and document processing."""
    st.subheader("  Upload a PDF Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file:
        st.success("PDF uploaded successfully!")

        if st.session_state.document_vector_index is None:
            with st.spinner("Processing PDF..."):
                doc_text = load_pdf_text(uploaded_file)
                vector_index = get_vectorstore_from_text(doc_text)
                qa_chain, memory = get_qa_chain_with_memory(vector_index)

                st.session_state.document_content = doc_text
                st.session_state.document_vector_index = vector_index
                st.session_state.conversational_qa_chain = qa_chain
                st.session_state.chat_memory = memory

            st.success("PDF processed and ready to explore.")
        else:
            st.info("A document is already processed. Upload a new one to replace it.")

# ---------------------------- #
#        Chat Interface        #
# ---------------------------- #

def chat_interface():
    """Provide a conversational Q&A interface for the uploaded document."""
    st.divider()
    st.subheader("  Ask Questions About the Document")

    with st.form("chat_form", clear_on_submit=True):
        question = st.text_input("Your question:")
        submit = st.form_submit_button("Ask")

    if submit and question:
        if st.session_state.conversational_qa_chain:
            with st.spinner("Thinking..."):
                response = st.session_state.conversational_qa_chain.run({"question": question})
            st.session_state.chat_history.append(("You", question))
            st.session_state.chat_history.append(("AI", response))
        else:
            st.warning("Please upload and process a PDF before asking questions.")

    if st.button("  Clear Chat"):
        st.session_state.chat_history = []
        st.experimental_rerun()

    if st.session_state.chat_history:
        st.markdown("###   Chat History")
        for speaker, message in st.session_state.chat_history:
            st.markdown(f"**{speaker}:** {message}")

# ---------------------------- #
#         Tools Section        #
# ---------------------------- #

def document_tools():
    """Provide utilities like summary, MCQ, and study plan generation."""
    st.divider()
    st.subheader("  Document Tools")

    # Summary
    if st.button("  Generate Summary"):
        if st.session_state.document_content:
            with st.spinner("Generating summary..."):
                summary = get_custom_response(summary_prompt, st.session_state.document_content)
            st.write(summary)
        else:
            st.warning("Upload a PDF first.")

    # MCQs
    if st.button("  Create MCQs"):
        if st.session_state.document_content:
            with st.spinner("Generating MCQs..."):
                mcqs = get_custom_response(mcq_prompt, st.session_state.document_content)
            st.write(mcqs)
        else:
            st.warning("Upload a PDF first.")

    # Study Plan
    if st.button("  Suggest Study Plan"):
        if st.session_state.document_content:
            with st.spinner("Creating plan..."):
                plan = get_custom_response(plan_prompt, st.session_state.document_content)
            st.write(plan)
        else:
            st.warning("Upload a PDF first.")

# ---------------------------- #
#            Main App          #
# ---------------------------- #

st.set_page_config(page_title=" PDF Assistant", layout="wide")
st.title(" PDF Assistant")

init_session_state()
upload_pdf()

if st.session_state.document_vector_index:
    chat_interface()
    document_tools()
else:
    st.info("Upload a PDF to get started.")
    chat_interface()
