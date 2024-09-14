import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


analyzer = SentimentIntensityAnalyzer()

def perform_sentiment_analysis_on_video(text: str) -> dict:
    return analyzer.polarity_scores(text)

def perform_sentiment_analysis_on_comments(comments: pd.Series) -> pd.DataFrame:
    comment_sentiments = comments.apply(analyzer.polarity_scores)
    sentiment_df = pd.DataFrame(comment_sentiments.tolist())
    return pd.concat([comments.reset_index(drop=True), sentiment_df], axis=1)

# data = pd.read_csv('bitchute_news_data.csv')
# data['video_text'] = data['title'] + " " + data['description']

# data['video_sentiment'] = data['video_text'].apply(perform_sentiment_analysis_on_video)

# comment_sentiment_df = perform_sentiment_analysis_on_comments(data['comments'])