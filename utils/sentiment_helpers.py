from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import plotly.express as px
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt

analyzer = SentimentIntensityAnalyzer()

def text_preprocessing(text):
    lemmatizer = WordNetLemmatizer()
    url_pattern = r"((http://)[^ ]*|(https://)[^ ]*|(www\.)[^ ]*)"
    user_pattern = r"@[^\s]+"
    entity_pattern = r"&.*;"
    neg_contraction = r"n't\W"
    non_alpha = "[^a-z]"
    cleaned_text = text.lower()
    cleaned_text = re.sub(neg_contraction, " not ", cleaned_text)
    cleaned_text = re.sub(url_pattern, " ", cleaned_text)
    cleaned_text = re.sub(user_pattern, " ", cleaned_text)
    cleaned_text = re.sub(entity_pattern, " ", cleaned_text)
    cleaned_text = re.sub(non_alpha, " ", cleaned_text)
    tokens = word_tokenize(cleaned_text)

    word_tag_tuples = pos_tag(tokens, tagset="universal")
    tag_dict = {"NOUN": "n", "VERB": "v", "ADJ": "a", "ADV": "r"}
    final_tokens = []
    for word, tag in word_tag_tuples:
        if len(word) > 1:
            if tag in tag_dict:
                final_tokens.append(lemmatizer.lemmatize(word, tag_dict[tag]))
            else:
                final_tokens.append(lemmatizer.lemmatize(word))
    return " ".join(final_tokens)
    
def highest_sentiment_score(text):
    scores = analyzer.polarity_scores(text)
    
    scores.pop('compound', 'neu')
    highest_sentiment = max(scores, key=scores.get)
    
    return scores[highest_sentiment]

def highest_sentiment(text):
    scores = analyzer.polarity_scores(text)
    
    scores.pop('compound', 'neu')
    highest_sentiment = max(scores, key=scores.get)
    
    return highest_sentiment

def predict_sentiment(data):
    data["Cleaned Text"] = data["Text"].apply(text_preprocessing)
    data = data[(data["Cleaned Text"].notna()) & (data["Cleaned Text"] != "")]
    data["Score"] = data["Cleaned Text"].apply(highest_sentiment_score)
    data["Sentiment"] = data["Cleaned Text"].apply(highest_sentiment)
    
    return data


def plot_sentiment(data):
    sentiment_count = data["Sentiment"].value_counts()
    fig = px.pie(values=sentiment_count.values, names=sentiment_count.index)
    return fig

def plot_wordcloud(text, width=600, height=400):
    fig, ax = plt.subplots(figsize=(width/100, height/100))
    wordcloud_img = WordCloud(width=width, height=height, background_color='white', max_words=200, contour_width=3, contour_color='steelblue').generate(text)
    ax.imshow(wordcloud_img, interpolation='bilinear')
    ax.axis('off')
    
    return fig
