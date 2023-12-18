import pandas as pd
import gspread
import json
import streamlit as st
from google.oauth2 import service_account
import datetime
import os

from llama_index import download_loader
from pandasai.llm.openai import OpenAI

# pip install streamlit pandas gspread google-auth llama-index pandasai


st.set_page_config(page_title='HIDA Q&A', layout='wide')
st.markdown('#### HIDA Q&A')

os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']




SP_SHEET = 'フォームの回答 1'

# 秘密鍵jsonファイルから認証情報を取得
#第一引数　秘密鍵のpath　第二引数　どこのAPIにアクセスするか
#st.secrets[]内は''で囲むこと
#scpes 今回実際に使うGoogleサービスの範囲を指定
credentials = service_account.Credentials.from_service_account_info(st.secrets['gcp_service_account'], scopes=[ "https://www.googleapis.com/auth/spreadsheets", ])

#OAuth2のクレデンシャル（認証情報）を使用してGoogleAPIにログイン
gc = gspread.authorize(credentials)

# IDを指定して、Googleスプレッドシートのワークブックを取得
sh = gc.open_by_key(st.secrets['FILE_KEY'])

# シート名を指定して、ワークシートを選択
worksheet = sh.worksheet(SP_SHEET)

data= worksheet.get_all_values()

# スプレッドシートをDataFrameに取り込む
df = pd.DataFrame(data, columns=data[0])

df2= df[['question', 'answer']]

st.table(df2)

##### loader


# Sample DataFrame
df = pd.DataFrame({
    "country": ["United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan", "China"],
    "gdp": [21400000, 2940000, 2830000, 3870000, 2160000, 1350000, 1780000, 1320000, 516000, 14000000],
    "happiness_index": [7.3, 7.2, 6.5, 7.0, 6.0, 6.3, 7.3, 7.3, 5.9, 5.0]
})

llm = OpenAI()

PandasAIReader = download_loader("PandasAIReader")

# use run_pandas_ai directly 
# set is_conversational_answer=False to get parsed output
loader = PandasAIReader(llm=llm)
response = reader.run_pandas_ai(
    df, 
    "Which are the 5 happiest countries?", 
    is_conversational_answer=False
)
print(response)

# # load data with is_conversational_answer=False
# # will use our PandasCSVReader under the hood
# docs = reader.load_data(
#     df, 
#     "Which are the 5 happiest countries?", 
#     is_conversational_answer=False
# )

# # load data with is_conversational_answer=True
# # will use our PandasCSVReader under the hood
# docs = reader.load_data(
#     df, 
#     "Which are the 5 happiest countries?", 
#     is_conversational_answer=True
# )
