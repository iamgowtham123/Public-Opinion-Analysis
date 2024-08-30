import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
from textblob import TextBlob
from googletrans import Translator

# Initialize Translator
translator = Translator()

# Load API key from secrets
api_key = st.secrets["api_key"]

emoji_sentiment = {
    '😊': 'positive',
    '😐': 'neutral',
    '😞': 'negative',
    '😍': 'positive',
    '😡': 'negative',
    '😜': 'positive',
    '😔': 'negative',
    '😎': 'positive',
    '😳': 'neutral',
    '😭': 'negative',
    '😢': 'negative',
    '❤️': 'positive',
    '💔': 'negative',
    '😘': 'positive',
    '🔥': 'positive',
    '😖': 'negative',
    '😣': 'negative',
    '🤬': 'negative',
    '💩': 'negative',
    '🙈': 'positive',
    '🥰': 'positive',
    '👍': 'positive',
    '👎': 'negative',
    '🎉': 'positive',
    '🎊': 'positive',
    '🥳': 'positive',
    '🤩': 'positive'
}

def get_youtube_service(api_key):
    return build('youtube', 'v3', developerKey=api_key)

def search_videos(youtube, hashtag, max_results):
    request = youtube.search().list(
        part="snippet",
        maxResults=max_results,
        q=f"#{hashtag}",
        type="video",
    )
    response = request.execute()
    return [item['id']['videoId'] for item in response['items']]

def translation(comment):
    translated_text = translator.translate(comment, dest='en').text
    return translated_text
    
def get_video_comments(youtube, video_id, max_comments, translate=False):
    comments = []
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_comments,
            textFormat="plainText"
        )
        response = request.execute()

        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            if translate:
                comment = translation(comment)
            comments.append(comment)

    except HttpError as e:
        if e.resp.status == 403 and 'commentsDisabled' in str(e):
            st.warning(f"Comments are disabled for video ID: {video_id}. Skipping...")
        else:
            raise e
    return comments

def clean_text(text):
    text = re.sub(r'http\S+', '', text)  # remove URLs
    text = re.sub(r'@\w+', '', text)  # remove mentions
    text = re.sub(r'#\w+', '', text)  # remove hashtags
    text = re.sub(r'[^A-Za-z\s]', '', text)
    return text

def analyze_sentiment(comments):
    sentiment_summary = {'positive': 0, 'neutral': 0, 'negative': 0}
    
    for comment in comments:
        cleaned_comment = clean_text(comment)
        analysis = TextBlob(cleaned_comment)
        
        text_sentiment = 'neutral'
        if analysis.sentiment.polarity > 0:
            text_sentiment = 'positive'
        elif analysis.sentiment.polarity < 0:
            text_sentiment = 'negative'
        
        emoji_sentiment_found = None
        for emoji, sentiment in emoji_sentiment.items():
            if emoji in comment:
                emoji_sentiment_found = sentiment
        
        final_sentiment = emoji_sentiment_found or text_sentiment
        sentiment_summary[final_sentiment] += 1
    
    return sentiment_summary

def generate_wordcloud(comments):
    cleaned_comments = [clean_text(comment) for comment in comments]
    all_comments = ' '.join(cleaned_comments)
    
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_comments)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis('off')
    st.pyplot(plt)

def main1(hashtag, api_key, max_videos, max_comments, translate=False):
    youtube = get_youtube_service(api_key)
    video_ids = search_videos(youtube, hashtag, max_videos)
    all_comments = []
    
    for video_id in video_ids:
        comments = get_video_comments(youtube, video_id, max_comments, translate)
        all_comments.extend(comments)
    
    if all_comments:
        sentiment_summary = analyze_sentiment(all_comments)
        generate_wordcloud(all_comments)
        
        total_comments = len(all_comments)
        st.write(f"Total Comments: {total_comments}")
        st.write(f"Positive: {sentiment_summary['positive']} ({(sentiment_summary['positive']/total_comments)*100:.2f}%)")
        st.write(f"Neutral: {sentiment_summary['neutral']} ({(sentiment_summary['neutral']/total_comments)*100:.2f}%)")
        st.write(f"Negative: {sentiment_summary['negative']} ({(sentiment_summary['negative']/total_comments)*100:.2f}%)")
    else:
        st.warning("No comments were found.")

def main():
    st.title("Public Opinion Analysis Software")
    
    mode = st.radio("Analyze by:", ("By Video Link", "By Hashtag"))
    
    if mode == "By Video Link":
        video_link = st.text_input("Enter the video link:")
        max_comments = st.number_input("Number of comments to fetch:", min_value=1, value=100)
        translate = st.checkbox("Translate comments to English")
        
        if st.button("Analyze"):
            if video_link:
                video_id = video_link.split("v=")[-1].split("&")[0]
                youtube = get_youtube_service(api_key)
                comments = get_video_comments(youtube, video_id, max_comments, translate)
                
                if comments:
                    generate_wordcloud(comments)
                    sentiment_summary = analyze_sentiment(comments)
                    
                    total_comments = len(comments)
                    st.write(f"Total Comments: {total_comments}")
                    st.write(f"Positive: {sentiment_summary['positive']} ({(sentiment_summary['positive']/total_comments)*100:.2f}%)")
                    st.write(f"Neutral: {sentiment_summary['neutral']} ({(sentiment_summary['neutral']/total_comments)*100:.2f}%)")
                    st.write(f"Negative: {sentiment_summary['negative']} ({(sentiment_summary['negative']/total_comments)*100:.2f}%)")
                else:
                    st.warning("No comments were found.")
            else:
                st.error("Please enter a valid video link.")
    
    elif mode == "By Hashtag":
        hashtag = st.text_input("Enter a hashtag:")
        max_videos = st.number_input("Number of videos to search:", min_value=1, value=5)
        max_comments = st.number_input("Number of comments per video:", min_value=1, value=100)
        translate = st.checkbox("Translate comments to English")
        
        if st.button("Analyze"):
            if hashtag:
                main1(hashtag, api_key, max_videos, max_comments, translate)
            else:
                st.error("Please enter a valid hashtag.")

if __name__ == "__main__":
    main()
