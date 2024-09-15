import streamlit as st
from utils.sentiment_helpers import predict_sentiment, plot_sentiment, plot_wordcloud
from utils.file_reader import read_txt, read_docx, read_pdf
from utils.download_helpers import get_table_download_link
from utils.data_helpers import fetch_report_data, display_bar_chart
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns
import networkx as nx


def generate_report_page():
    st.title("Generate Report")
    st.header("Search Filters")
        
    text_filter = st.text_input('Text Filter (Title/Description)')
    date_from = st.date_input('Date From')
    date_to = st.date_input('Date To')
    hashtags = st.text_input('Hashtags')
    sentiment = st.selectbox('Sentiment', ['All', 'Positive', 'Neutral', 'Negative'])
    ner = st.text_input('Named Entity Recognition')

    if st.button('Generate Report'):
        report_data = fetch_report_data(text_filter, date_from, date_to, hashtags, sentiment, ner)
        if report_data:
            st.subheader("Report Results")
            display_bar_chart(report_data['top_bigrams'], 'Top 5 Bi-Grams')
            display_bar_chart(report_data['top_trigrams'], 'Top 5 Tri-Grams')
            display_bar_chart(report_data['top_named_entities'], 'Top 5 NER')
            display_bar_chart(report_data['top_hashtags'], 'Top 5 Hashtags')

            st.subheader("Word Cloud")
            st.pyplot(plot_wordcloud(report_data['word_cloud_data'], 800, 400))

            st.subheader("Recommended Videos")
            st.write(report_data['recommended_videos'])

            st.subheader("Top Influencers")
            display_bar_chart(report_data['top_influencers'], 'Top Influencers by Engagement Rate')

            st.subheader("Sentiment Distribution")
            labels = [item['sentiment'] for item in report_data['sentiment_distribution']]
            values = [item['percentage'] for item in report_data['sentiment_distribution']]
            fig = px.pie(
                names=labels, 
                values=values, 
                title="Sentiment Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.3 
            )
            st.plotly_chart(fig)

            st.subheader("Sentiment Over Time")
            sentiment_time_df = pd.DataFrame(report_data['sentiment_over_time'])
            fig = px.line(sentiment_time_df, x='date', y='sentiment_score_over_time', title="Average Sentiment Over Time")
            st.plotly_chart(fig)

            st.subheader("Engagement Over Time")
            engagement_time_df = pd.DataFrame(report_data['engagement_over_time'])
            fig = px.bar(engagement_time_df, x='date', y=['positive_engagement'], title="Engagement Over Time", barmode='group')
            st.plotly_chart(fig)
            
            st.subheader("Anomalies Detected")
            engagement_anomalies_df = pd.DataFrame(report_data['anomalies'].get('engagement_anomalies'))
            fig, ax = plt.subplots()
            sns.boxplot(data=engagement_anomalies_df, ax=ax)
            st.pyplot(fig)

            st.subheader("Anomalies Detected")
            freq_anomalies_df = pd.DataFrame(report_data['anomalies'].get('frequency_anomalies'))
            fig, ax = plt.subplots()
            sns.boxplot(data=freq_anomalies_df, ax=ax)
            st.pyplot(fig)
            
            st.subheader("Network Graph: Channels & Hashtags")
            channel_network = report_data['network_data']['channel_network']
            G_channels = nx.node_link_graph(channel_network)
            pos_channels = nx.spring_layout(G_channels)

            plt.figure(figsize=(10, 7))
            nx.draw(G_channels, pos_channels, with_labels=True, node_size=500, node_color='skyblue', font_size=10, font_weight='bold')
            st.pyplot(plt)

            st.subheader("Network Graph: Bigrams")
            bigram_network = report_data['network_data']['bigram_network']
            G_bigrams = nx.node_link_graph(bigram_network)
            pos_bigrams = nx.spring_layout(G_bigrams)

            plt.figure(figsize=(10, 7))
            nx.draw(G_bigrams, pos_bigrams, with_labels=True, node_size=500, node_color='lightgreen', font_size=10, font_weight='bold')
            st.pyplot(plt)

        else:
            st.write("No data available for the selected filters.")
        
        # st.write("Download the full report:")
        # st.markdown(get_table_download_link(sentiment_df, "sentiment_report.csv", "Download Report"))

