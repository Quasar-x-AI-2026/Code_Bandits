import os
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    WebBaseLoader
)
import json
from langchain_core.documents import Document
from dotenv import load_dotenv


#loading
all_documents = []

def load_who_json(path):
    docs = []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for entry in data:
        title = entry.get("title", "")
        summary = entry.get("summary", "")
        sections = entry.get("sections", {})
        url = entry.get("url", "")

        # Summary as one chunk
        if summary:
            docs.append(
                Document(
                    page_content=summary,
                    metadata={
                        "title": title,
                        "section": "Summary",
                        "source": url
                    }
                )
            )

        # Each section as a chunk
        for section_name, content in sections.items():
            if content.strip():
                docs.append(
                    Document(
                        page_content=content,
                        metadata={
                            "title": title,
                            "section": section_name,
                            "source": url,
                            "doc_type": "WHO_FACT_SHEET"
                        }
                    )
                )

    return docs


txt_loader = DirectoryLoader(
    path="docs",
    glob="**/*.txt",
    loader_cls=TextLoader
)
all_documents.extend(txt_loader.load())

pdf_loader = DirectoryLoader(
    path="docs",
    glob="**/*.pdf",
    loader_cls=PyPDFLoader
)
all_documents.extend(pdf_loader.load())

who_json_path = "docs/who_fact_sheets.json"

if os.path.exists(who_json_path):
    who_docs = load_who_json(who_json_path)
    all_documents.extend(who_docs)

all_documents.extend(who_docs)


#chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunked_documents = text_splitter.split_documents(all_documents)

#embedding+storing
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


INDEX_PATH = "faiss_index"

if os.path.exists(INDEX_PATH):
    vectorstore = FAISS.load_local(
        INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
else:
    vectorstore = FAISS.from_documents(chunked_documents, embeddings)
    vectorstore.save_local(INDEX_PATH)

retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 3,
        "fetch_k": 10,
        "lambda_mult": 0.3
    }
)

load_dotenv()
HF_TOKEN = os.getenv("hf_token")
# Create base LLM
base_llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
    # huggingfacehub_api_token=,
    huggingfacehub_api_token="HF_TOKEN",
    temperature=0.3,
    max_new_tokens=180
)

# Wrap as chat model
chat = ChatHuggingFace(llm=base_llm)

def build_query(user_input, history):
    if not history:
        return f"Health-related question: {user_input}"

    last_ai = ""

    for msg in reversed(history):
        if isinstance(msg, AIMessage):
            last_ai = msg.content
            break

    if last_ai:
        return (
            f"Previous response (for context only): {last_ai}\n"
            f"Current health-related question: {user_input}"
        )
    else:
        return f"Health-related question: {user_input}"


EMERGENCY_KEYWORDS = [
    "chest pain",
    "difficulty breathing",
    "breathlessness",
    "severe bleeding",
    "unconscious",
    "sudden weakness",
    "fits",
    "seizure",
    "high fever in baby",
    "suicidal",
    "self harm"
]

CRITICAL_KEYWORDS = [
    "chest pain", "difficulty breathing", "breathlessness",
    "severe bleeding", "unconscious", "seizure", "fits",
    "suicidal", "self harm", "stroke"
]

HIGH_KEYWORDS = [
    "high fever", "persistent vomiting", "severe pain",
    "shortness of breath", "blood in vomit"
]

MODERATE_KEYWORDS = [
    "fever", "headache", "cough", "dizziness",
    "stomach pain", "infection", "weakness"
]

def get_urgency(user_input: str):
    text = user_input.lower()

    if any(k in text for k in CRITICAL_KEYWORDS):
        return 3, "Critical"

    if any(k in text for k in HIGH_KEYWORDS):
        return 2, "High"

    if any(k in text for k in MODERATE_KEYWORDS):
        return 1, "Moderate"

    return 0, "Low"


def ask_rag(user_input: str,history: list) -> str:

    urgency_level, urgency_label = get_urgency(user_input)

    # Emergency override
    if urgency_level == 3:
        emergency_msg = (
            "⚠️ This may be a medical emergency.\n\n"
            "Please seek immediate medical care or contact local emergency services.\n"
            "If available, visit the nearest hospital or call an emergency helpline.\n\n"
            "This information is for general awareness and does not replace professional medical advice."
        )

        history.append(HumanMessage(content=user_input))
        history.append(AIMessage(content=emergency_msg))

        return {
            "answer": emergency_msg,
            "urgency_level": urgency_level,
            "urgency_label": urgency_label
        }
    query = build_query(user_input,history)
    retrieved_docs = retriever.invoke(query)

    MAX_CONTEXT_CHARS = 2000

    context = ""
    for doc in retrieved_docs:
        content = doc.page_content.strip()
        if len(context) + len(content) > MAX_CONTEXT_CHARS:
            break
        context += content + "\n\n"

    system_message = SystemMessage(
        content=(
            "You are a Preventive Healthcare Awareness Assistant.\n\n"
            "Your role is to provide general health information, symptom awareness, "
            "and guidance on when to seek professional medical help.\n\n"
            "STRICT RULES (must follow all):\n"
            "1. You must NOT diagnose diseases or name specific medical conditions as conclusions.\n"
            "2. You must NOT prescribe medicines, treatments, or dosages.\n"
            "3. You must NOT replace a doctor or medical professional.\n"
            "4. You may explain common symptoms in a general, educational manner.\n"
            "5. You must clearly state when a user should consult a healthcare professional.\n"
            "6. If information is not present in the context, say exactly:\n"
            "'I don't know based on the provided documents.'\n"
            "7. Keep responses calm, supportive, and concise.\n"
            "8. Do NOT use alarming language unless urgency is clearly indicated.\n\n"
            "9. Answer in 3-4 bullet points only"
            "10. Each bullet point must be one sentence"
            "11. maximum total length: 70-90 words"
            "12. do not add extra explanations"
            "Always include this disclaimer when relevant:\n"
            "'This information is for general awareness and does not replace professional medical advice.'\n\n"
            f"Context:\n{context}"
        )
    )

    messages = [system_message]
    messages.extend(history[-6:])
    messages.append(HumanMessage(content=user_input))

    response = chat.invoke(messages)

    history.append(HumanMessage(content=user_input))
    history.append(AIMessage(content=response.content))
                      
    return {"answer": response.content,
            "urgency_level": urgency_level,
            "urgency_label": urgency_label
        }

