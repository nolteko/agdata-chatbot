import streamlit as st
import pandas as pd
import openai
import requests
import io
import os
import matplotlib.pyplot as plt

# Set your OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# SAS URL to your Excel file on Azure
excel_url = "https://agdata1.blob.core.windows.net/datasets/Skyline%20for%20Power%20BI%202.xlsx?sp=r&st=2025-07-09T20:47:10Z&se=2025-07-31T04:47:10Z&spr=https&sv=2024-11-04&sr=b&sig=V1VCaAM7kin4649BVLRnOscR%2FLfn1UraiIYnS%2FkLvLI%3D"

# Load Excel from Azure Blob Storage
response = requests.get(excel_url)
df = pd.read_excel(io.BytesIO(response.content))

# Streamlit UI
st.title("🔍 Chat with Skyline Excel Data")
st.markdown("Ask any question about the data below:")

# Show a sample of the data
with st.expander("📄 Preview DataFrame"):
    st.dataframe(df.head())

# Get user input
question = st.text_input("💬 What do you want to know?")

if question:
    # Construct prompt
    sample_data = df.head(3).to_string(index=False)
    prompt = f"""
You are a helpful data analyst. A user has uploaded a dataset stored in a pandas DataFrame named `df`.
Here are the first few rows:
{sample_data}

Now answer the following question using Python code:
{question}

Respond with just the code block. If the answer requires a chart, use matplotlib or plotly and assign it to a variable named `fig`. Assume `df` is already loaded.
"""

    # Call OpenAI
    from openai import OpenAI

     client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

     response = client.chat.completions.create(
         model="gpt-4",
         messages=[
             {"role": "system", "content": "You write Python data analysis code using pandas."},
           {"role": "user", "content": prompt}
    ]
)

code = response.choices[0].message.content.strip()

    st.code(code, language="python")

    # Try to run the code
    try:
        exec_globals = {'df': df, 'plt': plt}
        exec(code, exec_globals)

        if 'fig' in exec_globals:
            st.pyplot(exec_globals['fig'])  # Show matplotlib figure
        elif 'result' in exec_globals:
            st.success("Result:")
            st.write(exec_globals['result'])

    except Exception as e:
        st.error(f"⚠️ Error executing code:\n{e}")
