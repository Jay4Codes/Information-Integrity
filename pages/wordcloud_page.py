import streamlit as st
from utils.sentiment_helpers import plot_wordcloud
from utils.file_reader import read_txt, read_docx, read_pdf, filter_stopwords
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from utils.download_helpers import get_image_download_link, get_table_download_link

def wordcloud_page():
    st.title("Word Cloud")
    st.subheader("📁 Upload a pdf, docx or text file to generate a word cloud")

    uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf", "docx"])
    
    if uploaded_file:
        if uploaded_file.type == "text/plain":
            text = read_txt(uploaded_file)
        elif uploaded_file.type == "application/pdf":
            text = read_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = read_docx(uploaded_file)
        else:
            st.error("File type not supported. Please upload a txt, pdf or docx file.")
            st.stop()

        words = text.split()
        word_count = pd.DataFrame({'Word': words}).groupby('Word').size().reset_index(name='Count').sort_values('Count', ascending=False)

        top_words = word_count['Word'].head(50).tolist()
        additional_stopwords = st.multiselect("Additional stopwords:", sorted(top_words))
        additional_stopwords = [additional_stopword.lower() for additional_stopword in additional_stopwords]

        text = filter_stopwords(words, additional_stopwords)

        if text:
            width = st.slider("Select Word Cloud Width", 400, 2000, 1200, 50)
            height = st.slider("Select Word Cloud Height", 200, 2000, 800, 50)

        st.pyplot(plot_wordcloud(text, width, height))
        
        format_ = st.selectbox("Select file format to save the plot", ["png", "jpeg", "svg", "pdf"])
        resolution = st.slider("Select Resolution", 100, 500, 300, 50)
        if st.button(f"Save as {format_}"):
            buffered = BytesIO()
            plt.savefig(buffered, format=format_, dpi=resolution)
            st.markdown(get_image_download_link(buffered, format_), unsafe_allow_html=True)
        
        st.subheader("Word Count Table")
        st.write(word_count)
        
        if st.button('Download Word Count Table as CSV'):
            st.markdown(get_table_download_link(word_count, "word_count.csv", "Click Here to Download"), unsafe_allow_html=True)
            