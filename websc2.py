from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import webbrowser
import tkinter as tk
from textblob import TextBlob
from googletrans import Translator
from PIL import Image, ImageTk

translator = Translator()
api_key = "AIzaSyCR1bptqJMt4HPa-xh4gxaYW1FFcw2Nq7k"
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
    '😖': 'negatuve',
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

def search_videos(youtube, hashtag):
    max_results=video_entry.get()
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
    
    

def get_video_comments(youtube, video_id):
    global var
    max_comments=comments_entry.get()
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
            if a==1:
                comment1 = translation(comment)
                comments.append(comment1)
            else:
                comments.append(comment)

    except HttpError as e:
        if e.resp.status == 403 and 'commentsDisabled' in str(e):
            print(f"Comments are disabled for video ID: {video_id}. Skipping...")
        else:
            raise e
    return comments

def clean_text(text):
    text = re.sub(r'http\S+', '', text)  # remove URLs
    text = re.sub(r'@\w+', '', text)  # remove mentions`
    text = re.sub(r'#\w+', '', text)  # remove hashtags
    #text = re.sub(r'[^A-Za-z\s\u0900-\u097F\u0B80-\u0BFF]', '', text)
    text = re.sub(r'[^A-Za-z\s]', '', text)
    
    return text

def analyze_sentiment(comments):
    global sentiment_summary
    sentiment_summary = {'positive': 0, 'neutral': 0, 'negative': 0}
    
    for comment in comments:
        cleaned_comment = clean_text(comment)
        #print(cleaned_comment)
        
        analysis = TextBlob(cleaned_comment)
        
        # Determine text sentiment
        text_sentiment = None
        if analysis.sentiment.polarity > 0:
            text_sentiment = 'positive'
        elif analysis.sentiment.polarity == 0:
            text_sentiment = 'neutral'
        else:
            text_sentiment = 'negative'
        
        # Check for emojis and determine sentiment
        emoji_sentiment_found = None
        for emoji, sentiment in emoji_sentiment.items():
            if emoji in comment:
                emoji_sentiment_found = sentiment
        
        # Final sentiment determination
        if emoji_sentiment_found:
            final_sentiment = emoji_sentiment_found
        else:
            final_sentiment = text_sentiment
        
        sentiment_summary[final_sentiment] += 1
    
    return sentiment_summary

def generate_wordcloud(comments):
    
    cleaned_comments = [clean_text(comment) for comment in comments]
    all_comments = ' '.join(cleaned_comments)
    
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_comments)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis('off')
    plt.show()

def main1(hashtag, api_key):
    global sentiment_summary
    global all_comments
    youtube = get_youtube_service(api_key)

    # Search for videos by hashtag
    video_ids = search_videos(youtube, hashtag)

    # Extract comments from these videos
    all_comments = []
    for video_id in video_ids:
        comments = get_video_comments(youtube, video_id)
        all_comments.extend(comments)
    
    sentiment_summary = analyze_sentiment(all_comments)
    
    if all_comments:
        generate_wordcloud(all_comments)
        display_the_sentiment()
    else:
        print("No comments were found")

def display_the_sentiment():
    global sentiment_root
    sentiment_root = tk.Tk()
    sentiment_root.title("Sentiment Analysis")
    sentiment_root.geometry("640x480")
    
    total_comments = len(all_comments)
    
    if total_comments > 0:
        positive_pct = (sentiment_summary['positive'] / total_comments) * 100
        neutral_pct = (sentiment_summary['neutral'] / total_comments) * 100
        negative_pct = (sentiment_summary['negative'] / total_comments) * 100
    else:
        positive_pct = neutral_pct = negative_pct = 0
    
    senlabel=tk.Label(sentiment_root,text=f"Total Comments: {total_comments}",font=("Helvetica", 36))
    senlabel.pack(pady=10)
    senlabel1=tk.Label(sentiment_root,text=f"Positive: {sentiment_summary['positive']} ({positive_pct:.2f}%)",font=("Helvetica", 36))
    senlabel1.pack(pady=10)
    senlabel3=tk.Label(sentiment_root,text=f"Neutral: {sentiment_summary['neutral']} ({neutral_pct:.2f}%)",font=("Helvetica", 36))
    senlabel3.pack(pady=10)
    senlabel2=tk.Label(sentiment_root,text=f"Negative: {sentiment_summary['negative']} ({negative_pct:.2f}%)",font=("Helvetica", 36))
    senlabel2.pack(pady=10)

    

def search_youtube(hashtag):
    youtube_search_url = f"https://www.youtube.com/results?search_query={hashtag}"
    webbrowser.open(youtube_search_url)

def process_hashtag(user_input):
    print(f"Received string: {user_input}")
    hashtag = user_input
    api_key = "AIzaSyCR1bptqJMt4HPa-xh4gxaYW1FFcw2Nq7k"
    search_youtube(hashtag)
    main1(hashtag, api_key)

def main2():
    global video_entry
    global comments_entry
    global root
    global variable
    global var
    root = tk.Tk()
    root.title("String Submission Example")
    root.geometry("1920x1080")

    label = tk.Label(root, text="Enter a hashtag:", font=("Helvetica", 36))
    label.pack(pady=50)

    entry = tk.Entry(root, width=50, font=("Helvetica", 20))
    entry.pack(pady=10)
    
    video_count=tk.Label(root,text="How many video you want to search", font=("Helvetica", 36))
    video_count.pack(pady=20)
    
    video_entry = tk.Entry(root, width=50, font=("Helvetica", 20))
    video_entry.pack(pady=10)
    
    
    comments_count=tk.Label(root,text="How many comments you want to search", font=("Helvetica", 36))
    comments_count.pack(pady=20)
    
    comments_entry = tk.Entry(root, width=50, font=("Helvetica", 20))
    comments_entry.pack(pady=10)
    

    

    def submit():
        global a
        a=0
        hashtag_input = entry.get()  
        process_hashtag(hashtag_input)
        
    def submit1():
        global a
        a=1
        hashtag_input = entry.get()  
        process_hashtag(hashtag_input)
        

    submit_button = tk.Button(root, text="Without Translation", font=("Helvetica", 16), command=submit)
    submit_button.pack(pady=10)
    
    translation_button=tk.Button(root,text="With Translation", font=("Helvetica", 16), command=submit1)
    translation_button.pack(pady=10)
    
    note=tk.Label(root,text="Note: Utilizing translation during the analysis process may lead to increased processing time, but it ensures more accurate results.",font=("Helvetica", 8))
    note.pack(pady=10)
    
    

    root.mainloop()

def extract_video_id_(videolink):
    global youtube
    global video_id
    video_id = videolink.split("v=")[-1]
    video_id = video_id.split("&")[0]
    youtube = get_youtube_service(api_key)
    print(video_id)
    return video_id


def extractcomments():
    global videolink
    global a
    global one_comments
    global sentiment_summary
    global all_comments
    a=0
    videolink=ventry.get()
    print(videolink)
    extract_video_id_(videolink)
    all_comments=get_video_comments(youtube, video_id)
    print(all_comments)
    
    sentiment_summary = analyze_sentiment(all_comments)
    
    if all_comments:
        generate_wordcloud(all_comments)
        display_the_sentiment()
    else:
        print("No comments were found")
    
    
################
def onevideo_t():
    global a
    global one_comments
    global sentiment_summary
    global all_comments
    a=1
    videolink=ventry.get()
    print(videolink)
    extract_video_id_(videolink)
    all_comments=get_video_comments(youtube, video_id)
    print(all_comments)
    
    sentiment_summary = analyze_sentiment(all_comments)
    
    if all_comments:
        generate_wordcloud(all_comments)
        display_the_sentiment()
    else:
        print("No comments were found")
    
def video_analysis():
    global ventry
    global vroot
    global videolink
    global comments_entry
    vroot=tk.Tk()
    vroot.title("By Video Link")
    vroot.geometry("1080x768")
    
    label=tk.Label(vroot,text="Enter the video link:",font=("Helvetica", 16))
    label.pack(pady=10)
    
    ventry=tk.Entry(vroot,width=40,font=("Helvetica", 16))
    ventry.pack(pady=10)
    
    label3=tk.Label(vroot,text="Enter the number of comments to fetch:",font=("Helvetica", 16))
    label3.pack(pady=10)
    
    comments_entry =tk.Entry(vroot,width=40,font=("Helvetica", 16))
    comments_entry.pack(pady=10)
    
    
    
    
    submit_button = tk.Button(vroot, text="Without Translation", font=("Helvetica", 16), command=extractcomments)
    submit_button.pack(pady=10)
    
    
    
    translation_button=tk.Button(vroot,text="With Translation", font=("Helvetica", 16), command=onevideo_t)
    translation_button.pack(pady=10)
    
    note=tk.Label(vroot,text="Note: Utilizing translation during the analysis process may lead to increased processing time, but it ensures more accurate results.",font=("Helvetica", 12))
    note.pack(pady=10)
    

    
    


    
    
def main():
    global mroot
    mroot=tk.Toplevel()
    mroot.title("Select the mode")
    mroot.geometry("640x480")
    
    label=tk.Label(mroot,text="Welcome to Public Opinion Analysis Software",font=("Helvetica", 20))
    label.pack(pady=5)
    
    label=tk.Label(mroot,text="Analyse by:",font=("Helvetica", 10))
    label.pack(pady=5)
    
    button=tk.Button(mroot,text="By Video Link",font=("Helvetica", 16),command=video_analysis)
    button.pack(pady=10)
    
    button2=tk.Button(mroot,text="By Hashtag",font=("Helvetica", 16),command=main2)
    button2.pack(pady=10)
    
    image = Image.open("image//You.png")  
    image = image.resize((150, 50), Image.Resampling.LANCZOS)  
    photo = ImageTk.PhotoImage(image)


    logo_label = tk.Label(mroot, image=photo)
    logo_label.image = photo  
    logo_label.pack(pady=10)
    
if __name__ == "__main__":
    main()
