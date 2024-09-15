import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

sentiment_mapping = {
    'All': '',
    'Positive': 'pos',
    'Neutral': 'neu',
    'Negative': 'neg'
}

def fetch_report_data(text_filter, date_from, date_to, hashtags, sentiment, ner):
        url = "http://127.0.0.1:8000/api/videos/generate_report/"
        sentiment_value = sentiment_mapping.get(sentiment, '')
        params = {
            'text': text_filter,
            'date_from': date_from,
            'date_to': date_to,
            'hashtags': hashtags,
            'sentiment': sentiment_value,
            'ner': ner
        }
        response = requests.get(url, params=params)
        return response.json()
    
def display_bar_chart(data, title):
    df = pd.DataFrame(data)
    print("shape", df.shape)
    if df.shape[0]:
        st.subheader(title)
        fig, ax = plt.subplots()
        sns.barplot(y=df.index, x=df[df.columns[0]], data=df, ax=ax, palette='Blues_d')
        st.pyplot(fig)
