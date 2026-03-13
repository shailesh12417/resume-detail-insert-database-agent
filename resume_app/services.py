import os
import json
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document


# load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

VECTOR_DB_PATH = "vector_store"

os.environ["GROQ_API_KEY"] = GROQ_API_KEY


# -----------------------------
# LLM MODEL (Groq)
# -----------------------------
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)


# -----------------------------
# EMBEDDING MODEL
# -----------------------------
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# -----------------------------
# VECTOR DATABASE
# -----------------------------
vector_db = Chroma(
    collection_name="resume_vectors",
    persist_directory=VECTOR_DB_PATH,
    embedding_function=embedding_model
)


# -----------------------------
# PROMPT TEMPLATE
# -----------------------------
resume_prompt = PromptTemplate(
    input_variables=["resume_text"],
    template="""
Extract the following information from the resume.

Return ONLY valid JSON.

Fields:
name
email
phone
github
linkedin
skills
experience

Resume:
{resume_text}
"""
)


# -----------------------------
# EXTRACT DATA FROM RESUME
# -----------------------------
def extract_resume_data(text):

    response = llm.invoke(
        resume_prompt.format(resume_text=text)
    )

    raw = response.content.strip()

    if raw.startswith("```"):
        raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)
    except Exception as e:
        print("JSON parsing error:", e)
        print("Model output:", raw)
        return {}


# -----------------------------
# CLEAN DATA BEFORE MYSQL
# -----------------------------
def safe_value(v):

    if v is None:
        return None

    if isinstance(v, list):

        cleaned = []

        for item in v:

            if isinstance(item, dict):
                cleaned.append(" ".join(str(x) for x in item.values()))
            else:
                cleaned.append(str(item))

        return ", ".join(cleaned)

    if isinstance(v, dict):
        return ", ".join(str(x) for x in v.values())

    return str(v)



# -----------------------------
# STORE EMBEDDINGS
# -----------------------------
def store_embeddings(text, filename):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_text(text)

    docs = []

    for chunk in chunks:
        docs.append(
            Document(
                page_content=chunk,
                metadata={"source": filename}
            )
        )

    vector_db.add_documents(docs)

    vector_db.persist()


# -----------------------------
# SEMANTIC SEARCH
# -----------------------------
def search_resume(query):

    results = vector_db.similarity_search(query, k=1)

    output = []

    for r in results:
        output.append({
            "source": r.metadata["source"],
            "text": r.page_content[:300]
        })

    return output