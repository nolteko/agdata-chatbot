import streamlit as st
import pandas as pd
import requests
import io
import matplotlib.pyplot as plt
from openai import OpenAI

# Load Excel data from Azure Blob Storage
excel_url = "https://agdata1.blob.core.windows.net/datasets/Skyline%20for%20Power%20BI%202.xlsx?sp=r&st=2025-07-09T20:47:10Z&se=2025-07-31T04:47:10Z&spr=https&sv=2024-11-04&sr=b&sig=V1VCaAM7kin4649BVLRnOscR%2FLfn1UraiIYnS%2FkLvLI%3D"
response = requests.get(excel_url)
df = pd.read_excel(io.BytesIO(response.content))

st.title("🔍 Chat with Skyline Excel Data")

# Optional preview
with st.expander("📁 Preview DataFrame"):
    st.dataframe(df)

# User prompt
prompt = st.text_input("💬 What do you want to know?", placeholder="Ask any question about the data below:")

if prompt:
    try:
        # Call OpenAI GPT-3.5
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
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
                st.pyplot(exec_globals['fig'])
            elif 'result' in exec_globals:
                st.success("Result:")
                st.write(exec_globals['result'])
        except Exception as e:
            st.error(f"Error in executing generated code: {e}")

    except Exception as e:
        st.error(f"OpenAI API Error: {e}")
