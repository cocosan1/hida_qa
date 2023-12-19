import pandas as pd
import gspread
import json
import streamlit as st
from google.oauth2 import service_account
import datetime
import os

from langchain.document_loaders import DataFrameLoader


# pip install streamlit pandas gspread google-auth langchain


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
df = pd.DataFrame(data[1:], columns=data[0])

#datetime型に変換
df['timestamp_temp'] = pd.to_datetime(df['タイムスタンプ'])

#時刻データを削除した列の新設 str化
df['timestamp'] = df['timestamp_temp'].map(lambda x: x.strftime('%Y-%m-%d'))

# 列の絞り込み
df2= df[['timestamp', 'question', 'answer']]

st.table(df2)



loader = DataFrameLoader(df) # page_content_column='answer'

docs = loader.load()

st.write(docs)

import bs4
from langchain import hub
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import WebBaseLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)

vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

prompt = hub.pull("rlm/rag-prompt")
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

rag_chain.invoke("ベンチの脚のサイズは？")

