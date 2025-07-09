import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import openai
import io
import requests

# Set your app title
st.set_page_config(page_title="Chat with Skyline Excel Data", layout="wide")
st.title("🔍 Chat with Skyline Excel Data")

# Load Excel data from URL or file
excel_url = "https://github.com/nolteko/agdata-chatbot/raw/main/skyline_crops.xlsx"  # <-- Replace with your file URL
response = requests.get(excel_url)
df = pd.read_excel(io.BytesIO(response.content))

# Preview data
with st.expander("📄 Preview DataFrame"):
    st.dataframe(df)

# Chat input
st.subheader("💬 What do you want to know?")
prompt = st.text_input("Ask any question about the data below:")

if prompt:
    try:
        # Call OpenAI using modern API
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You write Python data analysis code using pandas. "
                                              "If the answer requires a chart, use matplotlib and assign it to `fig`. "
                                              "Assume df is already loaded."},
                {"role": "user", "content": prompt}
            ]
        )

        code = response.choices[0].message.content.strip()
        st.code(code, language="python")

        # Try to execute the code
        try:
            exec_globals = {'df': df, 'plt': plt}
            exec(code, exec_globals)

            if 'fig' in exec_globals:
                st.pyplot(exec_globals['fig'])  # Show matplotlib figure
            elif 'result' in exec_globals:
                st.success("Result:")
                st.write(exec_globals['result'])

        except Exception as e:
            st.error(f"❌ Error while executing code: {e}")

    except Exception as e:
        st.error(f"❌ OpenAI API Error: {e}")
