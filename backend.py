import os
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.memory import ConversationBufferMemory

# Load environment variables from .env file
load_dotenv()
palm_api_key = os.getenv("YOUR_API_KEY") 

#     Configuration Constants
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
MAX_TEXT_FOR_PROMPT = 12000


def load_pdf_text(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        raw_text = "".join([page.extract_text() or "" for page in reader.pages])
        clean_text = raw_text.strip()

        if not clean_text:
            raise ValueError("No extractable text found in the PDF.")

        return clean_text

    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")


def get_vectorstore_from_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_text(text)

    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=palm_api_key
        )
    except Exception as e:
        raise RuntimeError(f"Failed to initialize embeddings: {e}")

    return FAISS.from_texts(chunks, embedding=embeddings)


def get_qa_chain_with_memory(vectorstore):
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,
            google_api_key=palm_api_key,
            streaming=False
        )
    except Exception as e:
        raise RuntimeError(f"Failed to initialize language model: {e}")

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
        verbose=False
    )

    return qa_chain, memory


def get_custom_response(prompt_template, full_text):
    if not full_text:
        raise ValueError("Empty text input provided.")

    # Limit input size for token safety
    if len(full_text) > MAX_TEXT_FOR_PROMPT:
        full_text = full_text[:MAX_TEXT_FOR_PROMPT]

    try:
        prompt = ChatPromptTemplate.from_template(prompt_template)
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,
            google_api_key=palm_api_key
        )
        chain = prompt | model | StrOutputParser()
        return chain.invoke({"text": full_text})

    except Exception as e:
        raise RuntimeError(f"Failed to generate custom response: {e}")
