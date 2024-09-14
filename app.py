import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.express as px
from io import BytesIO
from file_reader import *
from download_files import *
from sentiment_helpers import *
import requests
import seaborn as sns
import networkx as nx


def main():
    st.set_page_config(
        page_title="SimPPL", layout="wide", initial_sidebar_state="auto", page_icon="📄"
    )

    with st.sidebar:
        st.image("static/icon.png")
        st.title("SimPPL")
        selected_page = option_menu(
            None,
            ["Home", "Word Cloud", "Sentiment Analysis", "Generate Report"],
            icons=["house", "chat", "database", "report"],
            menu_icon="cast",
            default_index=0,
        )

    if selected_page == "Home":
        st.image("static/icon.png")
        st.title("SimPPL")
        st.subheader("Welcome to SimPPL")
        with st.expander("About this app", expanded=False):
            st.write(   
                "Intelligent"
            )
        
    if selected_page == "Word Cloud":
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
                
                st.subheader("Generated Word Cloud")
                fig, ax = plt.subplots(figsize=(width/100, height/100))
                wordcloud_img = WordCloud(width=width, height=height, background_color='white', max_words=200, contour_width=3, contour_color='steelblue').generate(text)
                ax.imshow(wordcloud_img, interpolation='bilinear')
                ax.axis('off')

            st.pyplot(fig)
            
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
                
    if selected_page == "Sentiment Analysis":
        st.title("Sentiment Analysis")
        
        scraped_data = pd.read_csv("merged_data.csv")
        
        data = pd.DataFrame(scraped_data)
        data["Text"] = data["title"] + data["description"]
        data = predict_sentiment(data)
        st.write(data)  

        def make_dashboard(data, bar_color, wc_color):
            col1, col2, col3 = st.columns([28, 34, 38])
            with col1:
                sentiment_plot = plot_sentiment(data)
                sentiment_plot.update_layout(height=350, title_x=0.5)
                st.plotly_chart(sentiment_plot, theme=None, use_container_width=True)
            with col2:
                top_unigram = get_top_n_gram(data, ngram_range=(1, 1), n=10)
                unigram_plot = plot_n_gram(
                    top_unigram, title="Top 10 Occuring Words", color=bar_color
                )
                unigram_plot.update_layout(height=350)
                st.plotly_chart(unigram_plot, theme=None, use_container_width=True)
            with col3:
                top_bigram = get_top_n_gram(data, ngram_range=(2, 2), n=10)
                bigram_plot = plot_n_gram(top_bigram, title="Top 10 Occuring Bigrams", color=bar_color)
                bigram_plot.update_layout(height=350)
                st.plotly_chart(bigram_plot, theme=None, use_container_width=True)

            col1, col2 = st.columns([60, 40])
            with col1:
                def sentiment_color(sentiment):
                    if sentiment == "Positive":
                        return "background-color: #1F77B4; color: white"
                    else:
                        return "background-color: #FF7F0E"

                st.dataframe(
                    data[["Sentiment", "Text"]].style.applymap(
                        sentiment_color, subset=["Sentiment"]
                    ),
                    height=350,
                )
            with col2:
                wordcloud = plot_wordcloud(data, colormap=wc_color)
                st.pyplot(wordcloud)

        adjust_tab_font = """
        <style>
        button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
            font-size: 20px;
        }
        </style>
        """

        st.write(adjust_tab_font, unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["All", "Positive 😊", "Negative ☹️"])
        with tab1:
            make_dashboard(data, bar_color="#54A24B", wc_color="Greens")
        with tab2:
            data = data.query("Sentiment == 'neu'")
            make_dashboard(data, bar_color="#1F77B4", wc_color="Blues")
        with tab3:
            data = data.query("Sentiment == 'Negative'")
            make_dashboard(data, bar_color="#FF7F0E", wc_color="Oranges")

    if (selected_page == "Generate Report"):
        st.title("Generate Report")
        st.header("Search Filters")
        
        sentiment_mapping = {
            'All': '',
            'Positive': 'pos',
            'Neutral': 'neu',
            'Negative': 'neg'
        }
        text_filter = st.text_input('Text Filter (Title/Description)')
        date_from = st.date_input('Date From')
        date_to = st.date_input('Date To')
        hashtags = st.text_input('Hashtags')
        sentiment = st.selectbox('Sentiment', ['All', 'Positive', 'Neutral', 'Negative'])
        ner = st.text_input('Named Entity Recognition')

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

        if st.button('Generate Report'):
            report_data = fetch_report_data(text_filter, date_from, date_to, hashtags, sentiment, ner)

            if report_data:
                st.subheader("Report Results")

                # Display top keywords, bi-grams, NER, and hashtags as horizontal bar charts
                def display_bar_chart(data, title):
                    df = pd.DataFrame(data)
                    st.subheader(title)
                    fig, ax = plt.subplots()
                    sns.barplot(y=df.index, x=df[df.columns[0]], data=df, ax=ax, palette='Blues_d')
                    st.pyplot(fig)

                display_bar_chart(report_data['top_keywords'], 'Top 5 Keywords')
                display_bar_chart(report_data['top_bigrams'], 'Top 5 Bi-Grams')
                display_bar_chart(report_data['top_ner'], 'Top 5 NER')
                display_bar_chart(report_data['top_hashtags'], 'Top 5 Hashtags')

                # Display Word Cloud
                st.subheader("Word Cloud")
                wordcloud = WordCloud(width=800, height=400).generate(report_data['word_cloud_data'])
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)

                # Display Recommended Videos
                st.subheader("Recommended Videos")
                st.write(report_data['recommended_videos'])

                # Display Top Influencers as a horizontal bar chart
                st.subheader("Top Influencers")
                display_bar_chart(report_data['top_influencers'], 'Top Influencers by Engagement Rate')

                # Display Sentiment Distribution as a pie chart
                st.subheader("Sentiment Distribution")
                sentiment_df = pd.DataFrame(list(report_data['sentiment_distribution'].items()), columns=['Sentiment', 'Count'])
                fig = px.pie(sentiment_df, names='Sentiment', values='Count')
                st.plotly_chart(fig)

                # Display Sentiment Over Time as a line chart
                st.subheader("Sentiment Over Time")
                sentiment_time_df = pd.DataFrame(report_data['sentiment_over_time'])
                print(sentiment_time_df)
                fig = px.line(sentiment_time_df, x='date', y='sentiment_score_over_time', title="Average Sentiment Over Time")
                st.plotly_chart(fig)

                # Display Engagement Over Time
                st.subheader("Engagement Over Time")
                engagement_time_df = pd.DataFrame(report_data['engagement_over_time'])
                fig = px.bar(engagement_time_df, x='date', y=['positive_engagement'], title="Engagement Over Time", barmode='group')
                st.plotly_chart(fig)
                
                st.subheader("Anomalies Detected")
                engagement_anomalies_df = pd.DataFrame(report_data['anomalies'].get('engagement_anomalies'))
                fig, ax = plt.subplots()
                sns.boxplot(data=engagement_anomalies_df, ax=ax)
                st.pyplot(fig)


                # Display Anomaly Detection using box plots
                st.subheader("Anomalies Detected")
                freq_anomalies_df = pd.DataFrame(report_data['anomalies'].get('frequency_anomalies'))
                fig, ax = plt.subplots()
                sns.boxplot(data=freq_anomalies_df, ax=ax)
                st.pyplot(fig)
                

                # Display Network Graph of Channels and Bi-grams
                st.subheader("Network Graph: Channels & Hashtags")
                channel_network = report_data['network_data']['channel_network']
                G_channels = nx.node_link_graph(channel_network)
                pos_channels = nx.spring_layout(G_channels)

                plt.figure(figsize=(10, 7))
                nx.draw(G_channels, pos_channels, with_labels=True, node_size=500, node_color='skyblue', font_size=10, font_weight='bold')
                st.pyplot(plt)

                # Display the bigram network
                st.subheader("Network Graph: Bigrams")
                bigram_network = report_data['network_data']['bigram_network']
                G_bigrams = nx.node_link_graph(bigram_network)
                pos_bigrams = nx.spring_layout(G_bigrams)

                plt.figure(figsize=(10, 7))
                nx.draw(G_bigrams, pos_bigrams, with_labels=True, node_size=500, node_color='lightgreen', font_size=10, font_weight='bold')
                st.pyplot(plt)

            else:
                st.write("No data available for the selected filters.")

if __name__ == "__main__":
    main()