import os
from dotenv import load_dotenv
from pypdf import PdfReader
from groq import Groq

load_dotenv()

import streamlit as st

try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

def load_documents(docs_folder="documents"):
    all_text = ""
    for file in os.listdir(docs_folder):
        if file.endswith(".pdf"):
            reader = PdfReader(os.path.join(docs_folder, file))
            for page in reader.pages:
                all_text += page.extract_text() + "\n"
    return all_text

def get_answer(question, context):
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