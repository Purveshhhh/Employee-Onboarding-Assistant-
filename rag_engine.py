import os
from dotenv import load_dotenv
from pypdf import PdfReader
from groq import Groq
import streamlit as st

# Load .env only for local use
load_dotenv()

def get_client():
    """Get Groq client with API key (works locally + Streamlit Cloud)"""
    import os
    import streamlit as st
    from groq import Groq

    api_key = None

    # Try Streamlit secrets (Cloud)
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

    # Fallback to local .env
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ API key not found. Add it in Streamlit Secrets or .env file.")

    return Groq(api_key=api_key)

def load_documents(docs_folder="documents"):
    all_text = ""
    
    if not os.path.exists(docs_folder):
        return "No documents found."

    for file in os.listdir(docs_folder):
        if file.endswith(".pdf"):
            reader = PdfReader(os.path.join(docs_folder, file))
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    all_text += text + "\n"

    return all_text


def get_answer(question, context):
    client = get_client()  # ✅ create client here (NOT at top)

    prompt = f"""You are a helpful HR Employee Onboarding Assistant.
Use the following company document information to answer the employee's question.
If the answer is not in the documents, say "I don't have that information. Please contact HR directly."
Always be friendly, helpful and professional.

Company Documents:
{context}

Employee Question: {question}

Answer:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content